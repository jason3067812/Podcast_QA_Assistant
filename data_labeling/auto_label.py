from openai import OpenAI
import json
import sys
import spacy
spacy.prefer_gpu()
import os
import string



def remove_punctuation(sentence):
    
    punctuation = string.punctuation
    
    while sentence and sentence[0] in punctuation:
        sentence = sentence[1:]
    
    while sentence and sentence[-1] in punctuation:
        sentence = sentence[:-1]
    
    return sentence



# Function to read a text file and return its content
def read_text_file(file_path):
    with open(file_path, 'r') as file:
        return file.read()



# Function to create a SQuAD format annotation from user inputs
def create_squad_annotation(title, text, questions_and_answers, sentences, threshold):
    squad_data = {
        "data": [
            {
                "title": title,
                "paragraphs": [
                    {
                        "context": text,
                        "qas": []
                    }
                ]
            }
        ]
    }

    for qa in questions_and_answers:
        question, answer = qa
        
        print("gpt4 question: ", question)
        print("gpt4 answer: ", answer)
        
        ans_start = text.find(answer)
        
        # first word use lowercase
        if ans_start == -1:
          
          lowercase_answer = answer[0].lower() + answer[1:]
          ans_start = text.find(lowercase_answer)
          
          
          # determine by sentence similarity (spacy)
          if ans_start == -1:
              
              similarities = []
              
              target_doc = nlp(answer)
              for sentence in sentences:
                  
                  doc = nlp(sentence)
                  similarity = doc.similarity(target_doc)
                  similarities.append(similarity)
              
              max_similarity = max(similarities)
              max_similarity_index = similarities.index(max_similarity)
              
              
              print("similarity: ", max(similarities))
              print("transcript: ", sentences[max_similarity_index])
              
              if max_similarity >= threshold:
                  print("Use this gpt response")
                  ans_start = text.find(sentences[max_similarity_index])
                  
              else:
                  
                  print("Skip this error gpt response")
                  ans_start = -1
              
              
              
          else:
              print("Find! The first word in transcript is lowercase.")
              
        else:
            print("Find! Completely match.")
              
              
        print()
        
        if ans_start == -1:
            continue

        
        squad_data["data"][0]["paragraphs"][0]["qas"].append({
            "question": question,
            "id": str(len(squad_data["data"][0]["paragraphs"][0]["qas"]) + 1),
            "answers": [
                {
                    "text": answer,
                    "answer_start": ans_start
                }
            ]
        })

    return squad_data

# post-processing function, if there are quotation marks then remove them
def remove_outer_quotes(input_str):
    if (input_str.startswith('"') and input_str.endswith('"')) or (input_str.startswith("'") and input_str.endswith("'")):
        return input_str[1:-1]
    else:
        return input_str
    


# Main function
def main(file_path, number, threshold):
    
    output_path = os.path.splitext(file_path)[0] + '.json'
    filename_with_extension = os.path.basename(file_path)
    title = os.path.splitext(filename_with_extension)[0]

  
    # read transcript
    file_contents = read_text_file(file_path)
    
  
    word_length = len(file_contents.split())
    print("Total Words in the transcript: ", word_length)


    # use spacy to split sentence
    doc = nlp(file_contents)
    sentences = []
    for sentence in doc.sents:
        sentences.append(sentence.text)
        
    print("Total sentences in the transcript: ", len(sentences))
        
        
    # prompt here
    prompt = f"Step1. Read this transcript below first: \n{file_contents}\nStep2. Now give me {number} questions and the precise reference sentence you find in the transcript. Don't ask same questions.\nRule1. There are some advertisement inside this transcript, you need to recognize them and don't use those information to ask question.\nRule2. You musn't paraphrase and change words, structure in the reference sentence. The reference sentence must be completely same and can find in the transcript.\nRule3. Your response should be this format below: \nQuestion: \nReference Sentence: \n\nQuestion: \nReference Sentence: \n\n"
    
    messages = [
    
        {"role": "user", "content": prompt}

    ]

    print()
    print("Running GPT-4 ==================================\n")

    completion = client.chat.completions.create(
        model=model_id,
        messages=messages,
    )

    response = completion.choices[0].message.content
    # print(response)



    lines = [line.strip() for line in response.split("\n") if line.strip()]


    # post-processing logic here
    questions_and_answers = []
    for line in lines:
        
        print(line)
        

        if "Question:" in line:
            print("q:")
            
            colon_index = line.index(':')

            # Extract the sentence after the first colon
            question = line[colon_index + 1:].strip()
            print(question)
            
            
        elif "Reference Sentence:" in line:
            print("a:")
            
            colon_index = line.index(':')

            # Extract the sentence after the first colon
            answer = line[colon_index + 1:].strip()
            
            # clean response here
            
            # clean head and tail punctuation marks
            answer = remove_punctuation(answer)
            
            # clean "..."
            answer = answer.replace("...", "")
            
            print(answer)
        
            questions_and_answers.append((question, answer))
            
        else:
            continue
     
        
    print()
    print("Post-processing ==================================\n")
    # Create SQuAD format annotation
    squad_data = create_squad_annotation(title, file_contents, questions_and_answers,sentences, threshold)

    # Output to a JSON file

    with open(output_path, 'w', encoding='utf-8') as output_file:
        json.dump(squad_data, output_file, indent=2)

    print(f"SQuAD format annotation saved to {output_path}")
  
  
if __name__ == "__main__":
    
    
    # load spacy
    spacy_model = "en_core_web_lg"
    nlp = spacy.load(spacy_model)


    # load openai api
    # use your own key
    api_key = ""
    client = OpenAI(api_key=api_key)
    
    model_id = "gpt-4-1106-preview" # $0.01 / 1K tokens, recommend this model, more precise and can input larger transcripts !!!!!!!!

        
    print("Using OpenAI model: ", model_id)
    print("Using spaCy model: ", spacy_model)
    
    
    path = r"C:\Users\ee527\Desktop\Big Data Analytics\final_project\podcast_transcript\5\Prosecuting Donald Trump A Primer.txt"
    
    # file_name, number of questions
    main(path, 15, 0.92)




