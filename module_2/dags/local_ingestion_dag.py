from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta, timezone
import os
from ingest_script import ingest_callable

# Set local timezone
local_tz = timezone(timedelta(hours=6))

# Parameters
trip_class = "yellow"
data_year_month = "{{ execution_date.add(years=-1).strftime('%Y-%m')}}"

# Set the correct download URL
url = f"https://d37ci6vzurychx.cloudfront.net/trip-data/{trip_class}_tripdata_{data_year_month}.parquet"

# Set local download directory
download_dir = f"{os.getenv('AIRFLOW_HOME')}/data"

# Set default arguments
default_args = {
    'start_date': datetime(2025, 1, 1, tzinfo=local_tz),
}

# Define the DAG
local_workflow = DAG(
    "dag_data_ingestion",
    default_args=default_args,
    schedule_interval="0 6 2 * *"
)

with local_workflow:
    # Task to download the file
    get_data_task = BashOperator(
        task_id='get_data',
        bash_command=f'curl -o {download_dir}/{trip_class}_{data_year_month}_data.parquet {url}'
    )

    # ingest data to postgres
    ingest_data_task = PythonOperator(
        task_id='ingest_data',
        python_callable=ingest_callable,
        op_kwargs={
            'user': os.getenv("POSTGRES_USER"),
            'password': os.getenv("POSTGRES_PASSWORD"),
            'host': 'postgres',
            'port': 5432,
            'db': os.getenv("POSTGRES_DB"),
            'table_name': os.getenv('POSTGRES_TABLE'),
            'file': f'{download_dir}/{trip_class}_{data_year_month}_data.parquet',
            'execution_date': '{{ execution_date }}'
        }
    )

    # Set task dependencies
    get_data_task >> ingest_data_task
