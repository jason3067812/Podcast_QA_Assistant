# Podcast_QA_Assistant

This is the final project for EECS 6893 Big Data Analytics

## Installation Instructions
0. To begin, first install all dependencies by running
``` pip install -r requirements.txt```

1. Next, run the following commands to install the necessary spaCy models
   - ``` python -m spacy download en_core_web_sm```
   -  ```python -m spacy download en_core_web_lg```
   -  ```python -m spacy download en_core_web_trf```

2. After, generate an API key for GPT-3.5. Instructions can be found [here](https://www.educative.io/answers/how-to-get-api-key-of-gpt-3).
3. Save the API key to a text file called txt.key at the top level of the repo.
4. Download the data from the [drive](https://drive.google.com/drive/folders/1HnAgR-6ecyo-7LBPSX1K46NLuAIR2WFI?usp=sharing<br>)
   -  create the folders: data/, data/embedded, data/chunked
   -  save the embedded data under the data/embedded folder
   -  save the chunked data under the data/chunked folder
6. Launch the system, run ```python system.py``` in your terminal. A GUI should appear and you can begin interacting with the chatbot.

## Author
1. Karen Jan: kj2546@columbia.edu
2. Ziyao Tang: zt2338@columbia.edu
3. Eric Chang: cc4900@columbia.edu
