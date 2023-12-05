import pandas as pd
import os
import pickle
import numpy as np
import math
from ci_constants import *
import string
import sys

# Operators; we need this to operate!
from airflow.providers.google.cloud.transfers.local_to_gcs import LocalFilesystemToGCSOperator

####################################################
# DEFINE PYTHON FUNCTIONS
####################################################
added = set()

def get_file_path(chunk_id):
    filename = "{}.pkl".format(chunk_id)
    return os.path.join(DATA_DIR, filename)


def _make_task_id_for_gsc(item_moving_to_gcs, podcast_name, i):
    return 'upload_{}_to_gcs_{}_{}'.format(item_moving_to_gcs, podcast_name, i)

def _make_task_id_for_gsc_lst(item_moving_to_gcs, podcast_name):
    return 'upload_{}_to_gcs_{}'.format(item_moving_to_gcs, podcast_name)

def _get_transcribe_task(fname):
    with open(DATA_DIR + fname, 'rb') as f:
        task = pickle.load(f)
    return task



def _move_to_cloud_storage_helper(podcast_name, fname, local_dir, item_moving_to_gcs, external_sensor, dag):
    global added
    bucket_name = 'base_data_podcaster'
    
    # Upload each transcribed file to GCS
    local_file_path_lst = []
    gcs_file_path_lst = []
    task_idd = _make_task_id_for_gsc_lst(item_moving_to_gcs, podcast_name)
    for root, dirs, files in os.walk(local_dir, podcast_name):
        for i, filename in enumerate(files):
            local_file_path = os.path.join(root, filename)
            local_file_path_lst.append(local_file_path)
            gcs_file_path = "{}/{}/{}".format(item_moving_to_gcs, podcast_name, filename)
            gcs_file_path_lst.append(gcs_file_path)
    
    gcs_file_path = "/{}/{}/".format(item_moving_to_gcs, podcast_name)
    print('gcs_file_path', gcs_file_path)
    upload_task = LocalFilesystemToGCSOperator(
        task_id=task_idd,
        src=local_file_path_lst,
        dst=gcs_file_path,
        bucket=bucket_name,
    )
    upload_task.set_upstream(external_sensor)
    return upload_task


def _move_full_transcripts_to_cloud_storage(podcast_name, fname, external_sensor, dag):
    local_dir = TRANSCRIBE_DIR
    item_moving_to_gcs = 'full'
    return _move_to_cloud_storage_helper(podcast_name, fname, local_dir, item_moving_to_gcs, external_sensor, dag)


def _move_chunked_transcripts_to_cloud_storage(podcast_name, fname, external_sensor, dag):
    local_dir = CHUNK_DIR
    item_moving_to_gcs = 'chunked'
    return _move_to_cloud_storage_helper(podcast_name, fname, local_dir, item_moving_to_gcs, external_sensor, dag)


def _move_embedded_transcripts_to_cloud_storage(podcast_name, fname, external_sensor, dag):
    local_dir = EMBEDDED_DIR
    item_moving_to_gcs = 'embedded'
    return _move_to_cloud_storage_helper(podcast_name, fname, local_dir, item_moving_to_gcs, external_sensor, dag)


def move_to_cloud_storage(podcast_name, fname, external_sensor, dag):
    move_chunked = _move_chunked_transcripts_to_cloud_storage(podcast_name, fname, external_sensor, dag)
    move_embedded = _move_embedded_transcripts_to_cloud_storage(podcast_name, fname, external_sensor, dag)
    final_tasks = [
            # move_full,
            move_chunked,
            move_embedded,           
        ]

    return final_tasks


if __name__ == '__main__':
    podcast_name = sys.argv[1]
    fname = sys.argv[2]
    move_to_cloud_storage(podcast_name, fname)