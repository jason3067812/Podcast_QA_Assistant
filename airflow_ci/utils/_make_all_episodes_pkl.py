import pickle

def main():
    with open('./filenames.txt', 'r') as f:
        all_ep_titles = f.read()

    all_ep_titles = all_ep_titles.split("\n")

    with open('./all_fetched_episodes.pkl', 'wb') as f2:
        pickle.dump(all_ep_titles, f2)

if __name__ == "__main__":
    main()