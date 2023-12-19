import math
BUCKET_NAME = 'base_data_podcaster'

DATA_DIR = '/home/kj2546/airflow/data/'
TRANSCRIBE_DIR = '/home/kj2546/airflow/transcribed/'
CHUNK_DIR = '/home/kj2546/airflow/chunked/'
EMBEDDED_DIR = '/home/kj2546/airflow/embedded/'

API_KEY = ''

PODCAST_ID_DIR = {
    'beyond_the_screenplay': 'f616d744c4ae4d4ba126711cac2fd4e2',
    'prosecuting_donald_trump': '626ce14412af499d811d046990b2a34c',
    'american_history_hit': '42887949c8724017afa36890c46203d2',
}

CHUNK_SIZE = 100
OVERLAP_SIZE = 50
