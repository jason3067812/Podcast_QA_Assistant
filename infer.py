from openai import OpenAI
import json
import sys
import os
import string




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




