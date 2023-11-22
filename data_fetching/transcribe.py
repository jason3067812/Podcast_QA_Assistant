import whisper
import pickle
import sys

from constants import *

def transcribe_and_local_save(fname):
    with open(DATA_DIR + fname + '.pkl', 'rb') as f:
        audio_url_lst = pickle.load(f)
    with open(DATA_DIR + str(fname) + '_episode_keys.pkl', 'rb') as f:
        audio_episode_num_lst = pickle.load(f)

    model = whisper.load_model('base')
    for i, audio_url in enumerate(audio_url_lst):
        result = model.transcribe(audio_url)
        ep_num = audio_episode_num_lst[i]
        with open('{}/{}/{}.txt'.format(TRANSCRIBE_DIR, fname, ep_num), 'w') as f:
            f.write(result['text'])

if __name__ == '__main__':
    audio_chunk_id = sys.argv[1]
    transcribe_and_local_save(audio_chunk_id)
