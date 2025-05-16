import re
from collections import defaultdict
from difflib import SequenceMatcher
import openai
import os
 
openai.api_key = os.getenv("OPENAI_API_KEY")
print("OpenAI API Key:", os.getenv("OPENAI_API_KEY")) 
def check_names(text, doc_name):
    name_pattern = re.compile(r"\b([A-Z][a-z]+\s[A-Z][a-z]+)\b")
    found_names = name_pattern.findall(text)
    name_groups = defaultdict(list)
    errors = []
 
    for name in found_names:
        base = name.split()[0]
        name_groups[base].append(name)
 
    for base, names in name_groups.items():
        if len(set(names)) > 1:
            clarification = query_llm_name_variance(set(names))
            errors.append({
                "Document": doc_name,
                "Location": "-",
                "Error Type": "Name Inconsistency",
                "Description": f"Variants found: {set(names)}",
                "Suggestion": clarification
            })
    return errors
 
def query_llm_name_variance(name_set):
    prompt = f"Are the following names potentially referring to the same person or entity? Suggest a consistent name if so:\n{name_set}"
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )
        print("LLM Response:", response) ##Note
        return response['choices'][0]['message']['content']
    except Exception:
        return "Could not resolve name variation via LLM."