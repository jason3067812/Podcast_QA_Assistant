from datetime import datetime, timedelta
import pandas as pd
import os
import pickle
import numpy as np
import math
from constants import *

# The DAG object; we'll need this to instantiate a DAG
from airflow import DAG

# Operators; we need this to operate!
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.operators.dummy import DummyOperator
from airflow.providers.google.cloud.transfers.local_to_gcs import LocalFilesystemToGCSOperator


####################################################
# DEFINE PYTHON FUNCTIONS
####################################################
added = set()

def get_file_path(chunk_id):
    filename = "{}.pkl".format(chunk_id)
    return os.path.join(DATA_DIR, filename)

def move_to_cloud_storage(audio_chunk_id):
    global added
    bucket_name = 'base_data_podcaster'
    with open(DATA_DIR + str(audio_chunk_id) + '_episode_keys.pkl', 'rb') as f:
        episodes = pickle.load(f)

    # Upload each transcribed file to GCS
    upload_audio_id_files = []
    for ep in episodes:
        f = '{}.txt'.format(ep)
        local_file_path = os.path.join(TRANSCRIBE_DIR, str(audio_chunk_id), f)
        gcs_file_path = "beyond_the_screenplay/{}".format(f)
        task_idd = 'upload_to_gcs_{}'.format(f)
        if task_idd in added:
            continue
        else:
            upload_task = LocalFilesystemToGCSOperator(
                task_id=task_idd,
                src=local_file_path,
                dst=gcs_file_path,
                bucket=bucket_name,
            )
            upload_audio_id_files.append(upload_task)
            added.add(task_idd)
    return upload_audio_id_files

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
    'get_audio_data',
    default_args=default_args,
    description='transcribe {}'.format(PODCAST_NAME),
    schedule_interval="0 10 * * *", # run at 10 am
    start_date=datetime(2021, 1, 1),
    catchup=False,
    tags=['example'],
    concurrency=100
) as dag:

##########################################
# DEFINE AIRFLOW OPERATORS
##########################################
    # fetch audio url and pkl it
    fetch_audio_lst = [
        BashOperator(
            task_id='fetch_audio_url_{}'.format(i),
            bash_command='python /home/kj2546/airflow/dags/fetch_audio_2.py {}'.format(i),
            retries=3) for i in range(NUM_CHUNKS)
    ]

    transcribe_audio_lst = [
        BashOperator(
            task_id='transcribe_audio_{}'.format(i),
            bash_command='python /home/kj2546/airflow/dags/transcribe.py {}'.format(i),
            retries=3
        ) for i in range(NUM_CHUNKS)
    ]
    save_transcript_lst = [
        move_to_cloud_storage(i) for i in range(NUM_CHUNKS)
    ]

    

##########################################
# DEFINE TASKS HIERARCHY
##########################################
    for i in range(NUM_CHUNKS):
        fetch_audio_lst[i] >> transcribe_audio_lst[i] >> save_transcript_lst[i]



