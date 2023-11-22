import math
BUCKET_NAME = 'base_data_podcaster'

DATA_DIR = '/home/kj2546/airflow/data/'
TRANSCRIBE_DIR = '/home/kj2546/airflow/transcribed/'

API_KEY = 'bcb4b63d087f42b6942c85607dc2f711'
PODCAST_ID = 'f616d744c4ae4d4ba126711cac2fd4e2'
GCS_FOLDER_NAME = 'beyond_the_screenplay'
PODCAST_NAME = 'Beyond The Screenplay'
INITIAL_NEXT_EPISODE_PUB_DATE = 1689922800001

# for testing
NUM_AUDIO_FILES =  80
PAGE_SIZE = 10 # number of episodes returned per api call
NUM_CHUNKS = math.ceil(NUM_AUDIO_FILES / PAGE_SIZE)