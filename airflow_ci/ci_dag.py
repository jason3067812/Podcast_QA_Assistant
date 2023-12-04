from datetime import datetime, timedelta
import pandas as pd
import os
import pickle
import numpy as np
import math
from ci_constants import *
import string

# The DAG object; we'll need this to instantiate a DAG
from airflow import DAG

# Operators; we need this to operate!
from airflow.operators.bash import BashOperator
# from airflow.operators.python import PythonOperator
# from airflow.operators.dummy import DummyOperator
from airflow.providers.google.cloud.transfers.local_to_gcs import LocalFilesystemToGCSOperator


####################################################
# DEFINE PYTHON FUNCTIONS
####################################################
added = set()

def get_file_path(chunk_id):
    filename = "{}.pkl".format(chunk_id)
    return os.path.join(DATA_DIR, filename)



############################################
# DEFINE AIRFLOW DAG (SETTINGS + SCHEDULE)
############################################

default_args = {
    'owner': 'kjan',
    'depends_on_past': False,
    'email': ['kj2546@columbia.edu'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(seconds=30),
}

with DAG(
    'get_audio_data_ci',
    default_args=default_args,
    description='transcribe ci',
    schedule_interval="0 0 * * 1,4", # run at mon and thurs
    start_date=datetime(2021, 1, 1),
    catchup=False,
    tags=['example'],
    concurrency=100
) as dag:

##########################################
# DEFINE AIRFLOW OPERATORS
##########################################
    # fetch audio url and pkl it
    fetch_audio= BashOperator(
            task_id='fetch_audio_url',
            bash_command='python /home/kj2546/airflow/dags/ci_fetch_audio.py',
            retries=3)

    transcribe_audio = BashOperator(
            task_id='transcribe_audio',
            bash_command='python /home/kj2546/airflow/dags/ci_transcribe.py',
            retries=3
        )
    
    with open(DATA_DIR + 'transcribe_audio_task.pkl', 'wb') as f:
        pickle.dump(transcribe_audio, f)

    move_to_cloud_storage = [
        BashOperator(
            task_id='move_to_cloud_stoarge_{}'.format(podcast_name),
            bash_command='python /home/kj2546/airflow/dags/ci_post_to_gcs.py {} {}'.format(podcast_name, 'transcribe_audio_task.pkl'),
            retries=3
        ) for podcast_name in PODCAST_ID_DIR.keys()
    ]
    

##########################################
# DEFINE TASKS HIERARCHY
##########################################
    fetch_audio >> transcribe_audio >> move_to_cloud_storage



