from listennotes import podcast_api
import sys
import pickle
from ci_constants import *

def get_all_prior_fetched_set():
    with open(DATA_DIR + 'all_fetched_episodes.pkl'.format(podcast_name), 'rb') as f:
        all_fetched_episodse_urls = pickle.load(f)
    return all_fetched_episodse_urls
 

def fetch_audio_urls(podcast_name, podcast_id):
    all_fetched_episodse_titles = get_all_prior_fetched_set()
    client = podcast_api.Client(api_key=API_KEY)  
    response = client.fetch_podcast_by_id(id=podcast_id,
                                        sort='newest_first')
    response_json = response.json()
    episode_lst = response_json['episodes']

    audio_lst = []
    audio_ep_num_lst = []
    for i in range(len(episode_lst)):
        title = episode_lst[i]['title']
        audio_url = episode_lst[i]['audio']
        if '{}_{}'.format(podcast_name, title) not in all_fetched_episodse_titles: # only fetch new episodes
            audio_lst.append(audio_url)
            audio_ep_num_lst.append(title)

    fname = '{}.pkl'.format(podcast_name)
    with open(DATA_DIR + fname, 'wb') as f:
        pickle.dump(audio_lst, f)
    with open(DATA_DIR + str(podcast_name) + '_episode_keys.pkl', 'wb') as f2:
        pickle.dump(audio_ep_num_lst, f2)
    with open(DATA_DIR + 'all_fetched_episodes.pkl'.format(podcast_name), 'wb') as f3:
        for title in audio_ep_num_lst:
            all_fetched_episodse_titles.add('{}_{}'.format(podcast_name, title))
        pickle.dump(all_fetched_episodse_titles, f3)
    print('wrote', podcast_name)

if __name__ == '__main__':
    for podcast_name, podcast_id in PODCAST_ID_DIR.items():
        print(podcast_name, podcast_id)
        fetch_audio_urls(podcast_name, podcast_id)
