import nltk
import spacy
import os
import sys

nltk.download('punkt')
spacy.prefer_gpu()

SPACY = 'spacy'
SPACY_MODEL = "en_core_web_lg"
NLTK = 'nltk'
FOLDER = 'folder'
FILE = 'file'


def chunker(data, chunk_size, method):
    if method == SPACY:
        nlp = spacy.load(SPACY_MODEL)
        doc = nlp(data)
        sentences = []
        for sentence in doc.sents:
            sentences.append(sentence.text)
    elif method == NLTK:
        sentences = nltk.sent_tokenize(data)
    chunks = ['\n'.join(sentences[i:i + chunk_size]) for i in range(0, len(sentences), chunk_size)]
    
    return chunks, len(chunks)

def _save_chunked_file(chunk, filename, output_path, i):
    output_filename = output_path + "/" + filename
    with open(output_filename, 'w', encoding='utf-8') as file:
        file.write(chunk)
    print(f"Chunk {i + 1} save into {filename}")   

def chunk_file(file_path, output_path, method=SPACY, chunk_size=20):
    file_name_without_extension, file_extension = os.path.splitext(os.path.basename(file_path))
    with open(file_path, 'r') as file:
        content = file.read()
    chunks, chuncks_length = chunker(content, chunk_size, method)
    for i, chunk in enumerate(chunks):
        filename = f"{file_name_without_extension}_chunk_{i + 1}.txt"
        _save_chunked_file(chunk, filename, output_path, i)



def chunk_folder(dir_path, output_path, method=SPACY, chunk_size=20):
    for root, dirs, files in os.walk(dir_path):
        for filename in files:
            file_path = os.path.join(root, filename)
            chunk_file(file_path, output_path, method, chunk_size)

if __name__ == '__main__':
    chunk_size, method, dir_path, output_path, to_chunk  = sys.argv[1:]
    # chunk_size, method, dir_path, output_path, to_chunk = 20, SPACY, './input', './chunked_out', FOLDER
    if to_chunk == FOLDER:
        chunk_folder(dir_path, output_path, method, chunk_size)
    else:
        chunk_file(dir_path, output_path, method, chunk_size)
