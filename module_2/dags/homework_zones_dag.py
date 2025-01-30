from airflow import DAG
from datetime import datetime, timedelta, timezone
from airflow.operators.bash import BashOperator
import os
from google.cloud import storage
from airflow.operators.python import PythonOperator

# parameters
local_tz = timezone(timedelta(hours=6))
url = f"https://d37ci6vzurychx.cloudfront.net/misc/taxi_zone_lookup.csv"
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
    'start_date': datetime(2025, 1, 1, tzinfo=local_tz)
}

local_workflow = DAG(
    "zone_to_gcp_dag",
    default_args=default_args,
    catchup=False,
    schedule_interval=None
)

with local_workflow:

    # download data
    download_zone = BashOperator(
        task_id="download_zone",
        bash_command=f'curl -o {download_dir}/zone_data.parquet {url}'
    )

    upload_to_cloud = PythonOperator(
        task_id="upload_to_cloud",
        python_callable=upload_to_gcs,
        op_kwargs={
            'file_path': f'{download_dir}/zone_data.parquet',
            'destination_blob': f'data/zone_data.parquet'
        }
    )

    download_zone >> upload_to_cloud