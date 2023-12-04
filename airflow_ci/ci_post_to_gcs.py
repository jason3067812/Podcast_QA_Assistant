import pandas as pd
import os
import pickle
import numpy as np
import math
from ci_constants import *
import string
import sys

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

def _get_transcribe_task(fname):
    with open(DATA_DIR + fname, 'rb') as f:
        task = pickle.load(f)
    return task


def move_to_cloud_storage(podcast_name, fname):
    global added
    bucket_name = 'base_data_podcaster'
    with open(DATA_DIR + str(podcast_name) + '_episode_keys.pkl', 'rb') as f:
        episodes = pickle.load(f)

    # Upload each transcribed file to GCS
    upload_audio_id_files = []
    for i, ep in enumerate(episodes):
        f = '{}.txt'.format(_make_task_id_for_gsc(podcast_name, i))
        fname = '{}.txt'.format(ep)
        local_file_path = os.path.join(TRANSCRIBE_DIR, podcast_name, fname)
        gcs_file_path = "{}/{}".format(podcast_name, fname)
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
            upload_task.set_upstream(_get_transcribe_task(fname))
            upload_audio_id_files.append(upload_task)
            added.add(task_idd)
    return upload_audio_id_files

if __name__ == '__main__':
    podcast_name = sys.argv[1]
    fname = sys.argv[2]
    move_to_cloud_storage(podcast_name, fname)