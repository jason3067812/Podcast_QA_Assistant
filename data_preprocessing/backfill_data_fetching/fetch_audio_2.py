from listennotes import podcast_api
import sys
import pickle
from constants import *

def fetch_audio_urls(fetch_audio_chunk):
    weeks = lambda x: x*86400*1000*7
    nxt_ep_pub_date = INITIAL_NEXT_EPISODE_PUB_DATE - weeks(12)*int(fetch_audio_chunk)
    client = podcast_api.Client(api_key=API_KEY)  
    response = client.fetch_podcast_by_id(id=PODCAST_ID,
                                        next_episode_pub_date=nxt_ep_pub_date,
                                        sort='newest_first'
                                        )
    response_json = response.json()
    episode_lst = response_json['episodes']

    audio_lst = []
    audio_ep_num_lst = []
    for i in range(len(episode_lst)):
        title = episode_lst[i]['title']
        # skipping over patreon previews and administrative podcasts
        if "episode" not in title.lower():
            continue
        audio_url = episode_lst[i]['audio']
        audio_lst.append(audio_url)
        ep_num = title.split(' ')[1][:-1]
        audio_ep_num_lst.append(ep_num)

    fname = '{}.pkl'.format(fetch_audio_chunk)
    with open(DATA_DIR + fname, 'wb') as f:
        pickle.dump(audio_lst, f)
    with open(DATA_DIR + str(fetch_audio_chunk) + '_episode_keys.pkl', 'wb') as f2:
        pickle.dump(audio_ep_num_lst, f2)
    print('wrote', fetch_audio_chunk)

if __name__ == '__main__':
    audio_chunk_id = sys.argv[1]
    fetch_audio_urls(audio_chunk_id)
