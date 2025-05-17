import os 
import requests
from dotenv import load_dotenv

load_dotenv()

def query_groq(prompt, model="mixtral-8x7b-32768"):
    api_key = os.getenv("GROQ_API_KEY")
    url = "https://api.groq.com/openai/v1/chat/completions"
 
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
     
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."}, 
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"GROQ query failed. Error: {str(e)}"