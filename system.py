from openai import OpenAI



def pass_to_llm(title, chunk_info, query, client, model_id):
    
    print("input prompt: ")
    
    prompt = f"According to the following information: {chunk_info}\nAnswer the following question: {query}"

    print(prompt)


    messages = [
        
            {"role": "user", "content": prompt}

        ]
    
    
    completion = client.chat.completions.create(
    model=model_id,
    messages=messages,
    )
    
    response = completion.choices[0].message.content
    
    
    return response
    
    

def main():
    
    
    title = ""
    chunk_info = ""
    query = ""
    
    
    api_key = ""
    client = OpenAI(api_key=api_key)
    model_id = "gpt-3.5-turbo-1106"
    
    response = pass_to_llm(title, chunk_info, query, client, model_id)
    

    
    