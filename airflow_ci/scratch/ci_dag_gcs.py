from datetime import datetime, timedelta
import pandas as pd
import os
import pickle
import numpy as np
import math
from ci_constants import *

# The DAG object; we'll need this to instantiate a DAG
from airflow import DAG

# Operators; we need this to operate!
from airflow.operators.bash import BashOperator
# from airflow.operators.python import PythonOperator
# from airflow.operators.dummy import DummyOperator
from airflow.providers.google.cloud.transfers.local_to_gcs import LocalFilesystemToGCSOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow.sensors.external_task_sensor import ExternalTaskSensor
from airflow.utils.task_group import TaskGroup

from ci_post_to_gcs import move_to_cloud_storage

####################################################
# DEFINE PYTHON FUNCTIONS
####################################################
# added = set()

# def get_file_path(chunk_id):
#     filename = "{}.pkl".format(chunk_id)
#     return os.path.join(DATA_DIR, filename)


# def _make_task_id_for_gsc(item_moving_to_gcs, podcast_name, i):
#     return 'upload_{}_to_gcs_{}_{}'.format(item_moving_to_gcs, podcast_name, i)

# def _get_transcribe_task(fname):
#     with open(DATA_DIR + fname, 'rb') as f:
#         task = pickle.load(f)
#     return task

# def _get_fnames_to_post():
#     pass

# def _move_to_cloud_storage_helper(podcast_name, fname, local_dir, item_moving_to_gcs, external_sensor, dag):
#     global added
#     bucket_name = 'base_data_podcaster'
#     # with open(DATA_DIR + str(podcast_name) + '_episode_keys.pkl', 'rb') as f:
#     #     episodes = pickle.load(f)
    
#     # print('!!!!!! dir name', local_dir + podcast_name)
#     # foo = os.walk(local_dir + podcast_name)
#     # print('!!!!!!!!!! walk', list(foo))
    
#     # Upload each transcribed file to GCS
#     upload_audio_id_files = []
#     # for i, ep in enumerate(episodes):
#     for root, dirs, files in os.walk(local_dir, podcast_name):
#         # print('!!!!!!!!!', root, dir, files)
#         for i, filename in enumerate(files):
#             local_file_path = os.path.join(root, filename)
#             # fname = '{}.txt'.format(ep)
#             # local_file_path = os.path.join(TRANSCRIBE_DIR, podcast_name, fname)
#             task_idd = _make_task_id_for_gsc(item_moving_to_gcs, podcast_name, i)
#             gcs_file_path = "{}/{}/{}".format(item_moving_to_gcs, podcast_name, filename)
#             if task_idd in added:
#                 continue
#             else:
#                 # print('local path', local_file_path)
#                 # print('gcs path', gcs_file_path)
#                 upload_task = LocalFilesystemToGCSOperator(
#                     task_id=task_idd,
#                     src=local_file_path, # this can be a list of paths
#                     dst=gcs_file_path,
#                     bucket=bucket_name,
#                     # dag=dag,
#                 )
#                 upload_task.set_upstream(external_sensor)#_get_transcribe_task(fname))
#                 upload_audio_id_files.append(upload_task)
#                 added.add(task_idd)
#     # print('len', len(upload_audio_id_files))
#     return upload_audio_id_files


# def _move_full_transcripts_to_cloud_storage(podcast_name, fname, external_sensor, dag):
#     local_dir = TRANSCRIBE_DIR
#     item_moving_to_gcs = 'full'
#     return _move_to_cloud_storage_helper(podcast_name, fname, local_dir, item_moving_to_gcs, external_sensor, dag)


# def _move_chunked_transcripts_to_cloud_storage(podcast_name, fname, external_sensor, dag):
#     local_dir = CHUNK_DIR
#     item_moving_to_gcs = 'chunked'
#     return _move_to_cloud_storage_helper(podcast_name, fname, local_dir, item_moving_to_gcs, external_sensor, dag)


# def _move_embedded_transcripts_to_cloud_storage(podcast_name, fname, external_sensor, dag):
#     local_dir = EMBEDDED_DIR
#     item_moving_to_gcs = 'embedded'
#     return _move_to_cloud_storage_helper(podcast_name, fname, local_dir, item_moving_to_gcs, external_sensor, dag)


# def move_to_cloud_storage(podcast_name, fname, external_sensor, dag):
#     # with TaskGroup(group_id=podcast_name, dag=dag) as tg:
#         # move_full = _move_full_transcripts_to_cloud_storage(podcast_name, fname, external_sensor, dag)
#     move_chunked = _move_chunked_transcripts_to_cloud_storage(podcast_name, fname, external_sensor, dag)
#     move_embedded = _move_embedded_transcripts_to_cloud_storage(podcast_name, fname, external_sensor, dag)
#     final_tasks = [
#             # *move_full,
#             *move_chunked,
#             *move_embedded,
#         ]
#         # external_sensor.set_downstream(final_tasks)
#         # move_chunked.set_downstream(move)

#     # return tg
#     return final_tasks


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
    'save_data_to_gcs',
    default_args=default_args,
    description='transcribe ci',
    schedule_interval="0 6 * * 1,4", # run at mon and thurs @ 6am to give 6 hours for dependant dag to finish
    start_date=datetime(2021, 1, 1),
    catchup=False,
    tags=['example'],
    concurrency=100
) as dag:

##########################################
# DEFINE AIRFLOW OPERATORS
##########################################

    sensor = ExternalTaskSensor(
        task_id="Ext_Sensor_Task",
        external_dag_id="check_if_transcription_done",
        external_task_id="transcribe_audio",
        execution_delta = timedelta(hours=6),
        timeout=30)

    # with TaskGroup(group_id='group_id', dag=dag) as tg:
    # run_saving_task_group = move_to_cloud_storage('beyond_the_screenplay', 'fname', 'sensor', dag) 
    # foo = _move_chunked_transcripts_to_cloud_storage('beyond_the_screenplay', 'fname', 'external_sensor', dag)

        # dag=dag)
    # run_saving_task_group = [
    #     move_to_cloud_storage(podcast_name, 'fname', sensor, dag) for podcast_name in PODCAST_ID_DIR.keys()
    # ]
    # save_transcript_lst2 = [
    #     move_to_cloud_storage(podcast_name, 'fname', sensor, dag) for podcast_name in PODCAST_ID_DIR.keys()
    # ]
    move_to_cloud_storage_lst = [
        move_to_cloud_storage(podcast_name, 'transcribe_audio_task.pkl', sensor, 'dag') for podcast_name in PODCAST_ID_DIR.keys()
    ]
##########################################
# DEFINE TASKS HIERARCHY
##########################################
    # run_saving_task_group


