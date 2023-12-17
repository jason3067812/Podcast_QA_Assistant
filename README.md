# Podcast_QA_Assistant

This is the final project for EECS 6893 Big Data Analytics

## Installation Instructions
To begin, first install all dependencies by running
``` pip install -r requirements.txt```

Next, run the following commands to install the necessary spaCy models
``` python -m spacy download en_core_web_sm``` </br>
```python -m spacy download en_core_web_lg``` </br>
```python -m spacy download en_core_web_trf```</br>

To launch the system, do ```python system.py``` in your terminal. A GUI should appear and you can begin interacting with the chatbot.

1. install all dependencies in requirements.txt.<br>
2. download all data from: https://drive.google.com/drive/folders/1HnAgR-6ecyo-7LBPSX1K46NLuAIR2WFI?usp=sharing<br>
3. unzip data file and put it in the same location with system.py<br>
4. use eval.py to evaluate the output of gpt.<br>
5. use system.py to run the system and generate the user interface.<br>



## Author
1. Karen Jan: kj2546@columbia.edu
2. Ziyao Tang: zt2338@columbia.edu
3. Eric Chang: cc4900@columbia.edu
