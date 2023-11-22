import json
import sys

# Function to read a text file and return its content
def read_text_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def get_start_idx(context, substring):
    pass

# Function to create a SQuAD format annotation from user inputs
def create_squad_annotation(title, text, questions_and_answers):
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
        squad_data["data"][0]["paragraphs"][0]["qas"].append({
            "question": question,
            "id": str(len(squad_data["data"][0]["paragraphs"][0]["qas"]) + 1),
            "answers": [
                {
                    "text": answer,
                    "answer_start": text.find(answer)
                }
            ]
        })

    return squad_data

# Main function
def main(title):
    
    # Read the text from a file
    file_path = r"/Users/karenjan/Documents/columbia/big_data_analytics/pocaster/data/{}.txt".format(title)
    output_path = r"/Users/karenjan/Documents/columbia/big_data_analytics/pocaster/squad_data/{}.json".format(title)
    
    
    text = read_text_file(file_path)

    # Get user input for questions and answers
    questions_and_answers = []
    i = 1
    while True:
        question = input("{}. Enter a question (or type 'q' to quit): ".format(i))
        if question.lower() == 'q':
            break
        answer = input("{}. Enter the corresponding answer: ".format(i))
        questions_and_answers.append((question, answer))
        i += 1

    # Create SQuAD format annotation
    squad_data = create_squad_annotation(title, text, questions_and_answers)

    # Output to a JSON file
    
    with open(output_path, 'w', encoding='utf-8') as output_file:
        json.dump(squad_data, output_file, indent=2)

    print(f"SQuAD format annotation saved to {output_path}")

if __name__ == "__main__":
    ep_title = sys.argv[1]
    # ep_title = 100
    main(ep_title)
