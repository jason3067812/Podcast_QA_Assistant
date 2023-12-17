# Podcast_QA_Assistant

This is the final project for EECS 6893 Big Data Analytics

## Todos
- [x] finish embedding using transformers
- [x] modularize the embeddings 
- [x] get top n most similar documents to query
- [x] prompt engineering for gpt
- [x] system file (integration of parts) (majority is there; Ziyao to complete get_top_n_docs)
- [x] add embedding to airflow pipeline
- [x] UI system (make sure to include listennotes logo onto the api) (https://python.plainenglish.io/building-a-chatbot-with-django-and-chatgpt-9c0fdee2b162)
- [x] add overlap_size to chunk_file fn
- [ ] run experiments for chunk_size (number of sentences in chunk)
- [ ] run experiments for overlap_size (how much overlap should there be per chunk)
- [ ] make deck
- [ ] practice presentaiton
- [ ] record presentation

## Installation Instructions
To begin, first install all dependencies by running
``` pip install -r requirements.txt```

Next, run the following commands to install the necessary spaCy models
``` python -m spacy download en_core_web_sm```
```python -m spacy download en_core_web_lg```
```python -m spacy download en_core_web_trf```

1. install all dependencies in requirements.txt.<br>
2. download all data from: https://drive.google.com/drive/folders/1HnAgR-6ecyo-7LBPSX1K46NLuAIR2WFI?usp=sharing<br>
3. unzip data file and put it in the same location with system.py<br>
4. use eval.py to evaluate the output of gpt.<br>
5. use system.py to run the system and generate the user interface.<br>



## Author
1. Karen Jan: kj2546@columbia.edu
2. Ziyao Tang: zt2338@columbia.edu
3. Eric Chang: cc4900@columbia.edu
