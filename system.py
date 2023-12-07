import pickle
import sys
import numpy as np

from google.cloud import storage
# from pydrive.auth import GoogleAuth
# from pydrive.drive import GoogleDrive
from openai import OpenAI

from data_preprocessing.chunker import embed, find_similarity

BUCKET_NAME = 'base_data_podcaster'
CHUNKED_FOLDER = 'chunked/' + 'beyond_the_screenplay/' # TODO: REMOVE this extra beyond_the_screenplay once collapse all files into top level folder
EMBEDDED_FOLDER = 'embedded/'
ACCT_JSON_NAME = 'eecs6893-399001-57f9d9302900'

TESTING = 'smoll/'

def _get_blobs_from_gcs(folder_name):
    storage_client = storage.Client.from_service_account_json(ACCT_JSON_NAME + '.json')  # python-3 service account
    blobs = storage_client.list_blobs(BUCKET_NAME, prefix=folder_name)
    return blobs

def _get_fname_from_blob(blob):
    return blob.name.split('/')[-1].split('.')[0]

def fetch_pkl_content_from_gcs():
    blobs = _get_blobs_from_gcs(TESTING + EMBEDDED_FOLDER)
    vector_lst = []
    fname_lst = []
    for blob in blobs:
        if '.pkl' in blob.name:
            fname = _get_fname_from_blob(blob)
            fname_lst.append(fname)
            text = blob.download_as_string()
            vector_lst.append(pickle.loads(text))
    return vector_lst, fname_lst

def fetch_txt_content_from_gcs(lst_to_return=None):
    blobs = _get_blobs_from_gcs(TESTING + CHUNKED_FOLDER)
    text_lst = []
    fname_lst = []
    for blob in blobs:
        if '.txt' in blob.name:
            fname = _get_fname_from_blob(blob)
            if lst_to_return is None or fname in lst_to_return:
                fname_lst.append(fname)
                text = blob.download_as_string().decode('ASCII')
                text_lst.append(text)
    return text_lst, fname_lst


def get_top_n_docs(embedded_query, n, local_path=''):
    if len(local_path) == 0:
        embedded_docs, fname_lst = fetch_pkl_content_from_gcs()
    else:
        # get the files of embeddings from your local comp stored at local_path
        embedded_docs = []
        fname_lst = []
    
    # calc cosine distance
    similarity_scores = []
    for embed_doc in embedded_docs:
        similarity_scores.append(find_similarity(embedded_query, embed_doc))
    idx_of_top_n_docs = np.argsort(similarity_scores)[::-1][:n]
  
    # get top index of top n embedded docs (np.argmax probably)
    fname_of_chunks_to_fetch = fname_lst[idx_of_top_n_docs]
    if len(local_path) == 0:
        text_lst, _ = fetch_txt_content_from_gcs(fname_of_chunks_to_fetch)
    else:
        # get the text of the files from your local comp stored at local path
        text_lst = []
    return text_lst # in descending order by nature of np.argmax


def pass_to_llm(context_lst, query):
    api_key = ""
    client = OpenAI(api_key=api_key)
    model_id = "gpt-3.5-turbo-1106"

    prompt = f"According to the following information: {context_lst}\nAnswer the following question: {query}"
    messages = [
            {"role": "user", "content": prompt}
        ]
    completion = client.chat.completions.create(
    model=model_id,
    messages=messages,
    )
    response = completion.choices[0].message.content
    return response



def main(query, n=3):
    # embed query
    embedded_query = embed(query) 

    # top n docs based on query
    context_lst = get_top_n_docs(embedded_query, n)

    # pass query and chunked docs to llm fn - done / Eric's is integrated
    answer = pass_to_llm(context_lst, query)

    # return output
    return answer

if __name__ == "__main__":
    n = 3
    query = sys.argv[1]
    if len(sys.argv) == 3:
        n = sys.argv[2]
    answer = main(query)
    print(answer)

