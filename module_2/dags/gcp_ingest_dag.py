from airflow.models.dag import DAG
from datetime import datetime, timedelta
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
import os
import pandas as pd
from google.cloud import storage
from airflow.providers.google.cloud.operators.bigquery import BigQueryInsertJobOperator

# default arguments for dag
default_args = {
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 6,
    "retry_delay": timedelta(seconds=30)
}

# convert to parquet
def convert_to_parquet(input_path, output_path):
    df = pd.read_csv(input_path, encoding="utf-8")
    df.to_parquet(output_path, index=False)

# upload file to gcs
def upload_to_gcs(file_path, destination_blob):
    client = storage.Client()
    bucket = client.bucket(os.getenv("GCS_BUCKET"))
    blob = bucket.blob(destination_blob)
    blob.upload_from_filename(file_path)
    print(f"The file {file_path} has been uploaded to {os.getenv("GCS_BUCKET")}/{blob}")

#
with DAG (
    'gcp_ingest',
    default_args=default_args,
    description="A DAG to ingest data into GCP",
    schedule_interval=None,
    start_date=datetime(2025, 1, 26),
    catchup=False,
) as dag:

    # set local directory
    data_folder = os.path.join(os.getenv("AIRFLOW_HOME", "/opt/airflow"), "dags", "data")

    # get gcs

    # download file task
    download_file = BashOperator(
        task_id="download_data",
        depends_on_past=False,
        bash_command=f"curl -o {data_folder}/downloaded_data.csv https://www.stats.govt.nz/assets/Uploads/Annual-enterprise-survey/Annual-enterprise-survey-2023-financial-year-provisional/Download-data/annual-enterprise-survey-2023-financial-year-provisional-size-bands.csv"
    )

    # convert to parquet task
    convert_to_parquet = PythonOperator(
        task_id="convert_to_parquet",
        python_callable=convert_to_parquet,
        op_kwargs={
            'input_path': f'{data_folder}/downloaded_data.csv',
            'output_path': f'{data_folder}/converted_data.parquet'
        }
    )

    # upload to gcs
    upload_to_gcs=PythonOperator(
        task_id="upload_to_gcs",
        python_callable=upload_to_gcs,
        op_kwargs={
            'file_path': f'{data_folder}/converted_data.parquet',
            'destination_blob': 'data_uploaded.parquet'
        }
    )

    # load to bigquery
    load_to_bq=BigQueryInsertJobOperator(
        task_id="load_to_bq",
        configuration={
            "load": {
                "sourceUris": os.getenv("GCS_URI"),
                "destinationTable": {
                    "projectId": os.getenv("GOOGLE_CLOUD_PROJECT"),
                    "datasetId": os.getenv("BQ_DATASET"),
                    "tableId": "data_uploaded"
                },
                "sourceFormat": "PARQUET",
                "writeDisposition": "WRITE_TRUNCATE"
            }
        }
    )


download_file >> convert_to_parquet >> upload_to_gcs >> load_to_bq