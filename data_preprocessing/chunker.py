import nltk
import spacy
import os
import sys
import pickle
import numpy as np


nltk.download('punkt')
spacy.prefer_gpu()

SPACY = 'spacy'
SPACY_MODEL = "en_core_web_lg"
NLTK = 'nltk'
FOLDER = 'folder'
FILE = 'file'


def chunker_helper(sentences, chunk_size, overlap_size):
    chunks = []
    for i in range(0, len(sentences), chunk_size - overlap_size):
        chunk = sentences[i:i + chunk_size]
        concatenated_chunk = '\n'.join(chunk)  # Concatenate with '\n' separator
        chunks.append(concatenated_chunk)
    return chunks


def chunker(data, chunk_size, overlap_size, method):

    if method == SPACY:
        nlp = spacy.load(SPACY_MODEL)
        doc = nlp(data)
        sentences = []
        for sentence in doc.sents:
            sentences.append(sentence.text)
    elif method == NLTK:
        sentences = nltk.sent_tokenize(data)
        
    chunks = chunker_helper(sentences, chunk_size, overlap_size)
    
    return chunks, len(chunks)


def _save_chunked_file(chunk, filename, output_path, i):
    output_filename = output_path + "/" + filename
    with open(output_filename, 'w', encoding='utf-8') as file:
        file.write(chunk)
    print(f"Chunk {i + 1} save into {filename}")   


def chunk_file(file_path, output_path, method=SPACY, chunk_size = 100, overlap_size = 50):
    file_name_without_extension, file_extension = os.path.splitext(os.path.basename(file_path))
    print(file_path)
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    chunks, chuncks_length = chunker(content, chunk_size, overlap_size, method)
    for i, chunk in enumerate(chunks):
        filename = f"{file_name_without_extension}_chunk_{i + 1}.txt"
        _save_chunked_file(chunk, filename, output_path, i)


def chunk_folder(dir_path, output_path, method=SPACY, chunk_size = 100, overlap_size = 50):
    for root, dirs, files in os.walk(dir_path):
        for filename in files:
            file_path = os.path.join(root, filename)
            chunk_file(file_path, output_path, method, chunk_size)


# embeddings below
def embed(text,nlp):
    # Process the text
    doc = nlp(text)
    return doc._.trf_data.last_hidden_layer_state.data
    
    
def embed_file(file_path, output_path):
    file_name_without_extension, file_extension = os.path.splitext(os.path.basename(file_path))
    nlp = spacy.load('en_core_web_trf')

    with open(file_path, 'r') as file:
        text = file.read()
    
    embedding = embed(text, nlp)

    print(embedding)

    # doc = nlp(text)
    # embedding = doc.vector

    filename =  f"{file_name_without_extension}_embedded_.pkl"
    output_filename = output_path + "/" + filename

    with open(output_filename, 'wb') as out_file:
        pickle.dump(embedding, out_file)


def embed_folder(dir_path, output_path):
     for root, dirs, files in os.walk(dir_path):
        for filename in files:
            file_path = os.path.join(root, filename)
            embed_file(file_path, output_path)

def cosine(u, v):
    return np.dot(u, v) / (np.linalg.norm(u) * np.linalg.norm(v))


def find_similarity(file_path, query):
    file_name_without_extension, file_extension = os.path.splitext(os.path.basename(file_path))

    nlp = spacy.load('en_core_web_trf')
    doc = nlp(query)
    query_vec = doc.vector

    with open(file_path, 'rb') as file:
       data = pickle.load(file)
 
    sim = cosine(query_vec, data)
    print(file_name_without_extension," similarity = ", sim)



if __name__ == '__main__':
    
    
    #overlap_size, chunk_size, method, dir_path, output_path, to_chunk  = sys.argv[1:]
    # overlap_size = 50, chunk_size = 100, SPACY, './input', './chunked_out', FOLDER
    
    # overlap_size = 50
    # chunk_size = 100
    # method = SPACY
    # to_chunk = FOLDER
    # dir_path = "D:/GitHub/Podcast_QA_Assistant/full"
    # output_path = "D:/GitHub/Podcast_QA_Assistant/output"
    
    if to_chunk == FOLDER:
        chunk_folder(dir_path, output_path, method, chunk_size, overlap_size)
    else:
        chunk_file(dir_path, output_path, method, chunk_size, overlap_size)  
