import nltk
import spacy
import os
import sys
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim

nltk.download('punkt')
spacy.prefer_gpu()

SPACY = 'spacy'
SPACY_MODEL = "en_core_web_lg"
SPACY_EMBED_MODEL = 'en_core_web_trf'
SENTENCE_TRANSFORMER_MODEL = 'all-MiniLM-L6-v2'
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

def _save_chunked_meta(file_name_without_extension, output_path, num_chunks):
    to_write_path = '{}_meta.pkl'.format(file_name_without_extension)
    with open(output_path + '/' + to_write_path, 'wb') as f:
        pickle.dump(num_chunks, f)


def chunk_file(file_path, output_path, method=SPACY, chunk_size = 100, overlap_size = 50):
    file_name_without_extension, file_extension = os.path.splitext(os.path.basename(file_path))
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    chunks, chuncks_length = chunker(content, chunk_size, overlap_size, method)
    for i, chunk in enumerate(chunks):
        filename = f"{file_name_without_extension}_chunk_{i + 1}.txt"
        _save_chunked_file(chunk, filename, output_path, i)
        _save_chunked_meta(file_name_without_extension, output_path, chuncks_length)


def chunk_folder(dir_path, output_path, method=SPACY, chunk_size = 100, overlap_size = 50):
    for root, dirs, files in os.walk(dir_path):
        for filename in files:
            file_path = os.path.join(root, filename)
            chunk_file(file_path, output_path, method, chunk_size)


# embeddings below
def embed(text_lst, model=None):
    if model is None:
        model = SentenceTransformer(SENTENCE_TRANSFORMER_MODEL)
    return np.mean(model.encode(text_lst), axis=0)
    
    
def embed_file(file_path, output_path):
    model = SentenceTransformer(SENTENCE_TRANSFORMER_MODEL)
    file_name_without_extension, file_extension = os.path.splitext(os.path.basename(file_path))

    with open(file_path, 'r') as file:
        text_lst = file.read().split('\n')
    embedding = embed(text_lst, model)

    filename =  f"{file_name_without_extension}_embedded_.pkl"
    output_filename = output_path + "/" + filename

    with open(output_filename, 'wb') as out_file:
        pickle.dump(embedding, out_file)


def embed_folder(dir_path, output_path):
     for root, dirs, files in os.walk(dir_path):
        print(len(files))
        for i, filename in enumerate(files):
            if i%50 == 0:
                print(i)
            file_path = os.path.join(root, filename)
            embed_file(file_path, output_path)


def find_similarity(embed_query, embed_doc):
    sim = cos_sim(embed_query, embed_doc).item()
    return sim
