import pickle
import sys
import numpy as np
import os
import time
# from google.cloud import storage
# from pydrive.auth import GoogleAuth
# from pydrive.drive import GoogleDrive
from openai import OpenAI
from data_preprocessing.chunker import embed, find_similarity
import tkinter as tk
import requests
import json
from PIL import Image, ImageTk


BUCKET_NAME = 'base_data_podcaster'
CHUNKED_FOLDER = 'chunked/'
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
    print("fetch_pkl_content_from_gcs")
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
    print("fetch_txt_content_from_gcs")
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
    print("fetch_pkl_content_from_local_folder")
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
    
    print("fetch_txt_content_from_local_folder")
    text_lst = []
    fname_lst = []

    # Check all files in the specified local folder
    for fname in os.listdir(local_folder_path):

        
        if fname.endswith('.txt'):
            f = fname.split('.', 1)[0]
            if lst_to_return is None or f in lst_to_return:
             
                fname_lst.append(fname)
                with open(os.path.join(local_folder_path, fname), 'r', encoding="utf-8") as file:
                    
                    text_lst.append(file.read())
                    
                    
    print(fname_lst)

    return text_lst, fname_lst


def get_top_n_docs(embedded_query, n, local_folder_path=""):
    
    
    print("get_top_n_docs")
    if len(local_folder_path) == 0:
        embedded_docs, fname_lst = fetch_pkl_content_from_gcs()
    else:
        # get the files of embeddings from your local comp stored at local_path
        embedded_docs, fname_lst = fetch_pkl_content_from_local_folder(local_folder_path)
    
    # calc cosine distance
    similarity_scores = []
    for embed_doc in embedded_docs:
        similarity_scores.append(find_similarity(embedded_query, embed_doc))
    idx_of_top_n_docs = np.argsort(similarity_scores)[::-1][:n]
    
    
    print(idx_of_top_n_docs)
    
    
    # get top index of top n embedded docs (np.argmax probably)
    fname_of_chunks_to_fetch = [ fname_lst[x].replace('_embedded_.pkl', '') for x in idx_of_top_n_docs]
    
    print(fname_of_chunks_to_fetch)  
  
    
    if len(local_folder_path) == 0:
        text_lst, _ = fetch_txt_content_from_gcs(fname_of_chunks_to_fetch)
    else:
        # get the text of the files from your local comp stored at local path
        text_lst, _ = fetch_txt_content_from_local_folder(local_folder_path, lst_to_return=fname_of_chunks_to_fetch)
        
        
    return text_lst # in descending order by nature of np.argmax


def pass_to_llm(context_lst, query):
    
    
    print("pass_to_llm")
    api_key = ""
    client = OpenAI(api_key=api_key)
    model_id = "gpt-3.5-turbo-1106"
    # gpt-4-1106-preview, gpt-3.5-turbo-1106


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


def main(query, n):
    
    #embed query
    embedded_query = embed(query) 
    
    print(embedded_query.shape)

    start = time.time()
    # top n docs based on query
    context_lst = get_top_n_docs(embedded_query, n, "C:/Users/ee527/Desktop/testing")

    # pass query and chunked docs to llm fn - done / Eric's is integrated
    answer = pass_to_llm(context_lst, query)
    
    end = time.time()
    
    print(f"cost time: {end-start}")

    # return output
    return answer

if __name__ == "__main__":
    
    n = 3
    
    # Function to update the conversation
    def send():
        prompt = entry.get("1.0", 'end-1c')
       
        response = main([prompt],n)
        conversation.insert(tk.END, "\n\nYou: " + prompt + "\nPodCastGPT: " + response)
        entry.delete("1.0", tk.END)
        
    def clear():
        conversation.delete("1.0", tk.END)
        
        
    # Set up the window
    root = tk.Tk()
    root.title("What the Pod?")

    # Create a frame for conversation history and scrollbar
    frame = tk.Frame(root)
    frame.pack()

    # Create conversation history textbox
    conversation = tk.Text(frame, height=20, width=50)
    conversation.pack(side=tk.LEFT, fill=tk.Y)

    # Create a Scrollbar and attach it to conversation history
    scrollbar = tk.Scrollbar(frame, orient=tk.VERTICAL, command=conversation.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    conversation.config(yscrollcommand=scrollbar.set)

    # Create a prompt entry textbox
    entry = tk.Text(root, height=5, width=50)
    entry.pack()

    # Create a Send button
    send_button = tk.Button(root, text="Send", command=send)
    send_button.pack()
    
    # Create a Clear button
    clear_button = tk.Button(root, text="Clear", command=clear)
    clear_button.pack()

    # Create a photoimage object of the image in the path
    icon_path = os.path.join("icon", "listenotes.png")
    print(icon_path)
    image1 = Image.open(icon_path)
    test = ImageTk.PhotoImage(image1)
    label1 = tk.Label(image=test)
    label1.image = test
    # Position image
    label1.place(x=1, y=1)

    # Run the application
    root.mainloop()
    
    
    

