from sqlalchemy import create_engine
from time import time
import pyarrow.parquet as pq
import pandas as pd

def ingest_callable(user, password, host, port, db, table_name, file, execution_date):
    # For logging: show table name, file name, and execution date
    print(f"Table Name: {table_name}")
    print(f"File Path (Parquet): {file}")
    print(f"Execution Date: {execution_date}")

    # Create a connection to Postgres
    engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{db}')
    engine.connect()
    print('Connection established successfully, inserting data...')

    # Use PyArrow to open the Parquet file and iterate through it in batches
    parquet_file = pq.ParquetFile(file)
    batch_iter = parquet_file.iter_batches(batch_size=100000)

    # Process the first batch to create the table schema
    t_start = time()
    first_batch = next(batch_iter)
    df = first_batch.to_pandas()

    # Create the table with the columns from the first batch
    df.head(0).to_sql(name=table_name, con=engine, if_exists='replace')
    # Insert the first batch
    df.to_sql(name=table_name, con=engine, if_exists='append')

    t_end = time()
    print('Inserted the first chunk, took %.3f second(s).' % (t_end - t_start))

    # Process subsequent batches
    while True:
        t_start = time()
        try:
            batch = next(batch_iter)
        except StopIteration:
            print("All batches inserted, ingestion completed.")
            break

        df = batch.to_pandas()
        df.to_sql(name=table_name, con=engine, if_exists='append')

        t_end = time()
        print('Inserted another chunk, took %.3f second(s).' % (t_end - t_start))
