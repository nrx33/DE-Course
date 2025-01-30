from airflow import DAG
from datetime import datetime, timedelta, timezone
from airflow.operators.bash import BashOperator
import os

# Parameters
local_tz = timezone(timedelta(hours=6))
trip_class = "yellow"
data_year_month = "{{ ds[:7] }}"
url = f"https://d37ci6vzurychx.cloudfront.net/trip-data/{trip_class}_tripdata_{data_year_month}.parquet"
download_dir = f"{os.getenv('AIRFLOW_HOME')}/data"

# Define the DAG
default_args = {
    'start_date': datetime(2019, 1, 1, tzinfo=local_tz),
    'end_date': datetime(2020, 12, 31, tzinfo=local_tz)
}

local_workflow = DAG(
    "homework_workflow_ingest",
    default_args=default_args,
    schedule_interval="0 6 2 * *",
    catchup=True
)

with local_workflow:

    # download data
    download_data = BashOperator(
        task_id="download_data",
        bash_command=f'curl -o {download_dir}/{trip_class}_{data_year_month}_data.parquet {url}'
    )

    # task_2
    task_2 = BashOperator(
        task_id="task_2",
        bash_command="echo '{{ ds[:7] }}'"
    )

    download_data >> task_2