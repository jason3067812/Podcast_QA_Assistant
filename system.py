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
    final_text = "Read the following seperate documents first:\n"
    count = 0
    fname_lst = []
    for blob in blobs:
        if '.txt' in blob.name:
            fname = _get_fname_from_blob(blob)
            
            if lst_to_return is None or fname in lst_to_return:
                fname_lst.append(fname)
                text = blob.download_as_string().decode('ASCII')
                count+=1
                # chunk fushion here
                final_text = final_text + f"\ndocument {count}:\n"
    return final_text, fname_lst


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


def fetch_txt_content_from_local_folder(local_txt, lst_to_return=None):
    fname_lst = []
    final_text = "Read the following seperate documents first:\n"
    count = 0
    # Check all files in the specified local folder
    for fname in os.listdir(local_txt):
        if fname.endswith('.txt'):
            f = fname.split('.', 1)[0]
            if lst_to_return is None or f in lst_to_return:
                count+=1
                final_text = final_text + f"\ndocument {count}:\n"
                fname_lst.append(fname)
                with open(os.path.join(local_txt, fname), 'r', encoding="utf-8") as file:
                    sentence = file.read()
                    final_text = final_text + sentence
                
    return final_text, fname_lst


def get_top_n_docs(embedded_query, n, local_embedded, local_txt):
    if len(local_embedded) == 0:
        embedded_docs, fname_lst = fetch_pkl_content_from_gcs()
    else:
        embedded_docs, fname_lst = fetch_pkl_content_from_local_folder(local_embedded)
    # calc cosine distance
    similarity_scores = []
    for embed_doc in embedded_docs:
        similarity_scores.append(find_similarity(embedded_query, embed_doc))
    idx_of_top_n_docs = np.argsort(similarity_scores)[::-1][:n]
    fname_of_chunks_to_fetch = [ fname_lst[x].replace('_embedded_.pkl', '') for x in idx_of_top_n_docs]
    if len(local_txt) == 0:
        text_lst, _ = fetch_txt_content_from_gcs(fname_of_chunks_to_fetch)
    else:
        text_lst, fname_lst = fetch_txt_content_from_local_folder(local_txt, lst_to_return=fname_of_chunks_to_fetch)
    return text_lst


def pass_to_llm(context, query, n, api_key):
    client = OpenAI(api_key=api_key)
    model_id = "gpt-3.5-turbo-1106"
    # gpt-4-1106-preview, gpt-3.5-turbo-1106
    prompt = f"{context}\nNow according to the {n} documents you read, answer this question: {query}"
    messages = [
            {"role": "user", "content": prompt}
        ]
    completion = client.chat.completions.create(
    model=model_id,
    messages=messages,
    temperature = 0.5,
    seed = 1,
    ) 
    response = completion.choices[0].message.content
    return response


def infer(query, n, embedded_path, txt_path, api_key):
    #embed query
    embedded_query = embed(query) 
    start = time.time()
    # top n docs based on query
    context_lst = get_top_n_docs(embedded_query, n, embedded_path, txt_path)
    # pass query and chunked docs to llm fn - done / Eric's is integrated
    answer = pass_to_llm(context_lst, query, n, api_key)
    end = time.time()
    return answer

if __name__ == "__main__":
    # system initial
    # get gpt api key
    with open("key.txt", 'r', encoding='utf-8') as file:
        api_key = file.readline()
    # specify your top n parameter (n * chunk size cannot exceed 400 due to gpt3.5 token limitation) 
    n = 20
    # tkinter UI stuffs ============================================================================
    # Function to update the conversation
    first_interaction = True
    def send():
        prompt = entry.get("1.0", 'end-1c')
        selected_mode = mode_var.get()
        if selected_mode == "a":
            embedded_path = "./data/embedded/Screeplay/"
            text_path = "./data/text/Screeplay/"
        elif selected_mode == "b":
            embedded_path = "./data/embedded/DT/"
            text_path = "./data/text/DT/"
        elif selected_mode == "c":
            embedded_path = "./data/embedded/History/"
            text_path = "./data/text/History/"
        response = infer([prompt], n, embedded_path, text_path, api_key)
        conversation.insert(tk.END, "\n\nUser:\n" + prompt + "\n\nPodcastGPT:\n" + response)
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
    conversation.insert(tk.END, "Welcome to What the Pod ! Please wait for system initialization each time you choose a new podcast.\n")
    
    # Create a Scrollbar and attach it to conversation history
    scrollbar = tk.Scrollbar(frame, orient=tk.VERTICAL, command=conversation.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    conversation.config(yscrollcommand=scrollbar.set)

    # Create a prompt entry textbox
    entry = tk.Text(root, height=5, width=70)
    entry.pack(pady=10)

    # Create a Send button
    send_button = tk.Button(root, text="Send", command=send)
    send_button.pack()

    # Create a Clear button
    clear_button = tk.Button(root, text="Clear", command=clear)
    clear_button.pack(pady=10)

    # Create a label and radio buttons for selecting mode
    mode_var = tk.StringVar()
    mode_label = tk.Label(root, text="Choose one podcast you are interested in:")
    mode_label.pack(pady=10)

    mode_a_button = tk.Radiobutton(root, text="Beyond The Screenplay", variable=mode_var, value="a")
    mode_a_button.pack()

    mode_b_button = tk.Radiobutton(root, text="Prosecuting Donald Trump", variable=mode_var, value="b")
    mode_b_button.pack()

    mode_c_button = tk.Radiobutton(root, text="American History Hit", variable=mode_var, value="c")
    mode_c_button.pack()

    # Create a photoimage object of the image in the path
    icon_path = os.path.join("icon", "listenotes.png")
    image1 = Image.open(icon_path)
    test = ImageTk.PhotoImage(image1)
    label1 = tk.Label(image=test)
    label1.image = test
    # Position image
    label1.place(x=1, y=1)

    # Run the application
    root.mainloop()
