import math
BUCKET_NAME = 'base_data_podcaster'

DATA_DIR = '/home/kj2546/airflow/data/'
TRANSCRIBE_DIR = '/home/kj2546/airflow/transcribed/'

API_KEY = '06673b55481c47c3ac5636b2eddff44d'# Erics #'bcb4b63d087f42b6942c85607dc2f711'
# PODCAST_ID = 'f616d744c4ae4d4ba126711cac2fd4e2'
GCS_FOLDER_NAME = 'transcribed_data'
# PODCAST_NAME = 'Beyond The Screenplay'
# INITIAL_NEXT_EPISODE_PUB_DATE = 1689922800001

PODCAST_ID_DIR = {
    'beyond_the_screenplay': 'f616d744c4ae4d4ba126711cac2fd4e2',
    'prosecuting_donald_trump': '626ce14412af499d811d046990b2a34c',
    'american_history_hit': '42887949c8724017afa36890c46203d2',
}

# for testing
# NUM_AUDIO_FILES =  80
# PAGE_SIZE = 10 # number of episodes returned per api call
# NUM_CHUNKS = 1 #math.ceil(NUM_AUDIO_FILES / PAGE_SIZE)