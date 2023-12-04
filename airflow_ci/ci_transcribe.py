import whisper
import pickle
import sys

from ci_constants import *

def transcribe_and_local_save(podcast_name):
    with open(DATA_DIR + podcast_name + '.pkl', 'rb') as f:
        audio_url_lst = pickle.load(f)
    with open(DATA_DIR + str(podcast_name) + '_episode_keys.pkl', 'rb') as f:
        audio_episode_num_lst = pickle.load(f)

    # if len(audio_url_lst) > 0: # TODO: REMOVE CONDITION
    model = whisper.load_model('base')
    for i, audio_url in enumerate(audio_url_lst):
        result = model.transcribe(audio_url)
        ep_num = audio_episode_num_lst[i]
        with open('{}{}/{}.txt'.format(TRANSCRIBE_DIR, podcast_name, ep_num), 'w') as f:
            f.write(result['text'])

if __name__ == '__main__':
    for podcast_name, _ in PODCAST_ID_DIR.items():
        transcribe_and_local_save(podcast_name)
