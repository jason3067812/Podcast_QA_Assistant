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


def _make_task_id_for_gsc(podcast_name, i):
    return '{}_{}'.format(podcast_name, i)
    # ep = ep.replace(' ', '_').replace(':', '-').replace("'", '')
    # ep = ep.translate(str.maketrans('', '', string.punctuation))
    # return ep


# def move_to_cloud_storage_2(podcast_name):
#     global added
#     bucket_name = 'base_data_podcaster'
#     with open(DATA_DIR + str(podcast_name) + '_episode_keys.pkl', 'rb') as f:
#         episodes = pickle.load(f)

#     # Upload each transcribed file to GCS
#     upload_audio_id_files = []
#     for i, ep in enumerate(episodes):
#         f = '{}.txt'.format(_make_task_id_for_gsc(podcast_name, i))
#         local_file_path = os.path.join(TRANSCRIBE_DIR, podcast_name, f)
#         gcs_file_path = "{}/{}".format(podcast_name, f)
#         task_idd = 'upload_to_gcs_{}'.format(f)
#         if task_idd in added:
#             continue
#         else:
#             upload_task = LocalFilesystemToGCSOperator(
#                 task_id=task_idd,
#                 src=local_file_path,
#                 dst=gcs_file_path,
#                 bucket=bucket_name,
#             )
#             upload_audio_id_files.append(upload_task)
#             added.add(task_idd)
#     return upload_audio_id_files

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
    # save_beyond_the_screenplay = move_to_cloud_storage_2('beyond_the_screenplay')
    

    

##########################################
# DEFINE TASKS HIERARCHY
##########################################
    # for i in range(NUM_CHUNKS):
    fetch_audio >> transcribe_audio >> move_to_cloud_storage
    #  >> [ move_to_cloud_storage_2(i) for i in PODCAST_ID_DIR.keys() ] #[save_beyond_the_screenplay]

# TODO: either get sensor working or maybe try movign gcs into python operator (just move it to a new file and then call it)


