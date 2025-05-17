import os 
import requests
from dotenv import load_dotenv
import time

load_dotenv()

def query_groq(prompt, model="llama-3.3-70b-versatile"):
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise EnvironmentError("Missing GROQ_API_KEY environment variable.")
    
    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant for insurance document analysis."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3,
        "max_tokens": 1024
    }
    
    try:
        while True:
            response = requests.post(url, headers=headers, json=payload)

            if response.status_code == 429:
                retry_after = int(response.headers.get("retry-after", "1"))
                print(f"Rate limit exceeded. Retrying after {retry_after} seconds.")
                time.sleep(retry_after)
                continue
            elif not response.ok:
                raise Exception(f"GROQ query failed. Error: {response.status_code} {response.text}")

            return response.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"GROQ query failed. Error: {str(e)}"