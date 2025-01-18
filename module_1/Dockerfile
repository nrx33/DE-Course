FROM python:3.9-slim

# set working directory
WORKDIR /app

# install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl

# copy the required files to the docker container
COPY ingest_data.py /app/
COPY data/ /app/data/

# install python dependencies
RUN pip install pandas pyarrow sqlalchemy psycopg2

# run the python script with arguments
CMD ["python", "ingest_data.py"]