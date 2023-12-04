import nltk
nltk.download('punkt')
import spacy
spacy.prefer_gpu()
spacy_model = "en_core_web_lg"
import os



def chunker(data, chunk_size, method):
    
    
    if method == "spacy":
    
        nlp = spacy.load(spacy_model)
        doc = nlp(data)
        sentences = []
        for sentence in doc.sents:
            sentences.append(sentence.text)
            
    elif method == "nltk":
        
        sentences = nltk.sent_tokenize(data)
        
        
    chunks = ['\n'.join(sentences[i:i + chunk_size]) for i in range(0, len(sentences), chunk_size)]
        
        
    return chunks, len(chunks)


chunk_size = 20
method = "spacy"
directory_path = r"D:\GitHub\Podcast_QA_Assistant\data_preprocessing\system\input"
output_path = r"D:\GitHub\Podcast_QA_Assistant\data_preprocessing\system\output"

if not os.path.exists(output_path):
    os.makedirs(output_path)


for root, dirs, files in os.walk(directory_path):
    for filename in files:
        
        file_path = os.path.join(root, filename)
        
        file_name_without_extension, file_extension = os.path.splitext(os.path.basename(file_path))
        
        
        with open(file_path, 'r') as file:
            content = file.read()
            
            
        chunks, chuncks_length = chunker(content, chunk_size, method)
        
        
        for i, chunk in enumerate(chunks):
   
            filename = f"{file_name_without_extension}_chunk_{i + 1}.txt"
            
            output_filename = output_path + "/" + filename
            
            with open(output_filename, 'w', encoding='utf-8') as file:
                file.write(chunk)
            
            print(f"Chunk {i + 1} save into {filename}")
        
            
            





