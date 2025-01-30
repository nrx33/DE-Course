from airflow import DAG
from datetime import datetime, timedelta, timezone
from airflow.operators.bash import BashOperator
import os
from google.cloud import storage
from airflow.operators.python import PythonOperator

# parameters
local_tz = timezone(timedelta(hours=6))
data_year_month = "{{ ds[:7] }}"
url = f"https://d37ci6vzurychx.cloudfront.net/trip-data/fhv_tripdata_{data_year_month}.parquet"
download_dir = f"{os.getenv('AIRFLOW_HOME')}/data"

# upload file to gcs
def upload_to_gcs(file_path, destination_blob):
    client = storage.Client()
    bucket = client.bucket(os.getenv("GCS_BUCKET"))
    blob = bucket.blob(destination_blob)
    blob.upload_from_filename(file_path)
    print(f"The file {file_path} has been uploaded to {os.getenv("GCS_BUCKET")}/{blob}")


# dag setup
default_args = {
    'start_date': datetime(2019, 1, 1, tzinfo=local_tz),
    'end_date': datetime(2020, 12, 31, tzinfo=local_tz)
}

local_workflow = DAG(
    "fhv_to_gcp_dag",
    default_args=default_args,
    catchup=True,
    schedule_interval="0 6 2 * *",
)

with local_workflow:

    # download data
    download_fhv = BashOperator(
        task_id="download_fhv",
        bash_command=f'curl -o {download_dir}/fhv_{data_year_month}_data.parquet {url}'
    )

    upload_to_cloud = PythonOperator(
        task_id="upload_to_cloud",
        python_callable=upload_to_gcs,
        op_kwargs={
            'file_path': f'{download_dir}/fhv_{data_year_month}_data.parquet',
            'destination_blob': f'data/fhv_{data_year_month}_data.parquet'
        }
    )

    download_fhv >> upload_to_cloud