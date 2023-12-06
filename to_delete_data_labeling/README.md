# Data labeling for SQuAD format dataset

## 1. Supervised labeler
## 2. Unsupervised labeler
### powered by gpt api and spacy
### beta 1:
- initialized system pipeline
### beta 2 (11/21/2023 updated):
- revised prompt, finalized using gpt4 turbo instead of gpt3.5 and 4, fixed errors caused by punctuation and abbreviation, increased threshold to 0.95.
- new problems found: when gpt response is two sentences, spacy matching accuracy decreases
