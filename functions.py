
model = "gpt-35-turbo-16k"

def get_llm_response(client, messages):
    
    response = (
            client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.3,
                max_tokens=1024,
                timeout=20,
            )
            .choices[0]
            .message.content
        )
    return response
