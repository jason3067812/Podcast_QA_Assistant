import pickle
import numpy as np
import os
import time
from openai import OpenAI
from data_preprocessing.chunker import embed, find_similarity
import tkinter as tk
import requests
import json
from PIL import Image, ImageTk


BUCKET_NAME = 'base_data_podcaster'
CHUNKED_FOLDER = 'chunked/'
EMBEDDED_FOLDER = 'embedded/'
ACCT_JSON_NAME = ''


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


def fetch_pkl_content_from_local_folder(local_folder_path):
    vector_lst = []
    fname_lst = []

    # Check all files in the specified local folder
    for fname in os.listdir(local_folder_path):
        if fname.endswith('.pkl'):
            fname_lst.append(fname)
            with open(os.path.join(local_folder_path, fname), 'rb') as file:
                vector_lst.append(pickle.load(file))

    return vector_lst, fname_lst


def fetch_txt_content_from_local_folder(local_folder_path, lst_to_return=None):
    fname_lst = []
    final_text = "Read the following seperate documents first:\n"
    count = 0
    # Check all files in the specified local folder
    for fname in os.listdir(local_folder_path):
        if fname.endswith('.txt'):
            f = fname.split('.', 1)[0]
            if lst_to_return is None or f in lst_to_return:
                count+=1
                final_text = final_text + f"\ndocument {count}:\n"
                fname_lst.append(fname)

                with open(os.path.join(local_folder_path, fname), 'r', encoding="utf-8") as file:
                    sentence = file.read()
                    final_text = final_text + sentence
                    
    return final_text, fname_lst


def get_top_n_docs(embedded_query, n, local_embedded_path = "", local_txt_path = ""):
    if len(local_embedded_path) == 0:
        embedded_docs, fname_lst = fetch_pkl_content_from_gcs()
    else:
        embedded_docs, fname_lst = fetch_pkl_content_from_local_folder(local_embedded_path)
    
    # calc cosine distance
    similarity_scores = []
    for embed_doc in embedded_docs:
        similarity_scores.append(find_similarity(embedded_query, embed_doc))
    idx_of_top_n_docs = np.argsort(similarity_scores)[::-1][:n]
    fname_of_chunks_to_fetch = [ fname_lst[x].replace('_embedded_.pkl', '') for x in idx_of_top_n_docs]

    if len(local_txt_path) == 0:
        text_lst, _ = fetch_txt_content_from_gcs(fname_of_chunks_to_fetch)
    else:
        text_lst, _ = fetch_txt_content_from_local_folder(local_txt_path, lst_to_return=fname_of_chunks_to_fetch)
        
    return text_lst


def pass_to_llm(context, query, n, api_key):
    api_key = api_key
    client = OpenAI(api_key=api_key)
    model_id = "gpt-3.5-turbo-1106"
    prompt = f"{context}\nNow according to the {n} documents you read, answer this question: {query}"
    messages = [
            {"role": "user", "content": prompt}
        ]
    completion = client.chat.completions.create(
    model=model_id,
    messages=messages,
    temperature = 0,
    seed = 1,
    )
    response = completion.choices[0].message.content
    return response


def main(query, n, embedded_path, txt_path, api_key):
    #embed query
    embedded_query = embed(query) 
    start = time.time()

    # top n docs based on query
    context = get_top_n_docs(embedded_query, n, embedded_path, txt_path)

    # pass query and chunked docs to llm fn - done / Eric's is integrated
    answer = pass_to_llm(context, query, n, api_key)
    
    end = time.time()
    print(f"cost time: {end-start}")

    # return output
    return answer


if __name__ == "__main__":
    # standardized question
    level1 = ["What is one reason to use long scense with few cuts?","Did Mr. Trump sexually abuse Ms. Carroll?", "When did President Dwight D. Eisenhower hosted British Prime Minister Winston Churchill at the White House?"]
    level2 = ["What is a disadvantage of killing your main protagonist early in the film?", "Who thought the law didn't apply to him, and famously said that he could shoot someone in Fifth Avenue in your city of New York?", "Who first discovered gold on January 24, 1848, and where?"]
    level3 = ["Why was inside out able to pull at your heartstrings?", "How tall is Donald Trump?", "When did Boris Johnson serve as US president?"]
    
    if (len(level1) == len(level2)) and (len(level1) == len(level3)):
        print("testing data pass: ", len(level1))
    # top n parameter    
    n_list = [20]

    # input testing data
    embedded_data_path = "C:/Users/ee527/Downloads/embedded/nano_chunk"  
    txt_data_path = "C:/Users/ee527/Downloads/text/nano_chunk"          
    
    for fname in os.listdir(embedded_data_path):
        print("")
        print(f"now testing dataset: {fname} ==================================================================================================================")
        print("")
        
        for n in n_list:
            
            print("top n = ", n)
            print("")

            print("*********************** level 1 question ***********************\n")
            for prompt in level1:
                
                response = main([prompt],n, embedded_data_path+"/"+fname, txt_data_path+"/"+fname)
            
                print("")
                print("A:")
                print(response)
                print("")
              
            print("*********************** level 2 question ***********************\n")  
            for prompt in level2:
                
                response = main([prompt], n, embedded_data_path+"/"+fname, txt_data_path+"/"+fname)
    
                print("")
                print("A:")
                print(response)
                print("")
            
            print("*********************** level 3 question ***********************\n")
            for prompt in level3:
                
                response = main([prompt], n, embedded_data_path+"/"+fname, txt_data_path+"/"+fname)
            
                print("")
                print("A:")
                print(response)
                print("")