import whisper
import pickle
import sys

from ci_constants import *
from chunker import *

def _save_entire_transcript(result, podcast_name, ep_num):
    print('save entire transcript --', podcast_name)
    with open('{}{}/{}.txt'.format(TRANSCRIBE_DIR, podcast_name, ep_num), 'w') as f:
        f.write(result['text'])

def _chunk_and_save(podcast_name, ep_num):
    method = SPACY
    chunk_size = 20
    f_path = '{}{}/{}.txt'.format(TRANSCRIBE_DIR, podcast_name, ep_num)
    out_path_dir = '{}{}'.format(CHUNK_DIR, podcast_name, ep_num)
    print('chunk and save --', podcast_name)
    chunk_file(f_path, out_path_dir, method, chunk_size)

def _embed_and_save(podcast_name, ep_num):
    pass


def transcribe_and_local_save(podcast_name):
    with open(DATA_DIR + podcast_name + '.pkl', 'rb') as f:
        audio_url_lst = pickle.load(f)
    with open(DATA_DIR + str(podcast_name) + '_episode_keys.pkl', 'rb') as f:
        audio_episode_num_lst = pickle.load(f)

    model = whisper.load_model('base')
    for i, audio_url in enumerate(audio_url_lst):
        # result = model.transcribe(audio_url) # TODO: UNCOMMENT ME
        ep_num = audio_episode_num_lst[i]
        # _save_entire_transcript(result, podcast_name, ep_num)
        _chunk_and_save(podcast_name, ep_num)
        # _embed_and_save(podcast_name, ep_num)

if __name__ == '__main__':
    for podcast_name, _ in PODCAST_ID_DIR.items():
        transcribe_and_local_save(podcast_name)
