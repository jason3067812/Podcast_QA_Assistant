import nltk
import spacy
import os
import sys
import pickle

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
        chunks.append(chunk)
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
    with open(file_path, 'r') as file:
        content = file.read()
    chunks, chuncks_length = chunker(content, chunk_size, method, overlap_size)
    for i, chunk in enumerate(chunks):
        filename = f"{file_name_without_extension}_chunk_{i + 1}.txt"
        _save_chunked_file(chunk, filename, output_path, i)


def chunk_folder(dir_path, output_path, method=SPACY, chunk_size = 100, overlap_size = 50):
    
    for root, dirs, files in os.walk(dir_path):
        for filename in files:
            file_path = os.path.join(root, filename)
            chunk_file(file_path, output_path, method, chunk_size, overlap_size)


def embed_file(file_path, output_path):
    
    file_name_without_extension, file_extension = os.path.splitext(os.path.basename(file_path))
    nlp = spacy.load('en_core_web_lg')

    with open(file_path, 'r') as file:
        text = file.read()

    doc = nlp(text)
    embedding = doc.vector

    filename =  f"{file_name_without_extension}_embedded_.pkl"
    output_filename = output_path + "/" + filename

    with open(output_filename, 'wb') as out_file:
        pickle.dump(embedding, out_file)


def embed_folder(dir_path, output_path):
    
     for root, dirs, files in os.walk(dir_path):
        for filename in files:
            file_path = os.path.join(root, filename)
            embed_file(file_path, output_path)



if __name__ == '__main__':
    
    overlap_size, chunk_size, method, dir_path, output_path, to_chunk  = sys.argv[1:]
    # chunk_size, method, dir_path, output_path, to_chunk = 20, SPACY, './input', './chunked_out', FOLDER
    if to_chunk == FOLDER:
        chunk_folder(dir_path, output_path, method, chunk_size, overlap_size)
    else:
        chunk_file(dir_path, output_path, method, chunk_size, overlap_size)    
