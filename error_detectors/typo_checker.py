import language_tool_python
from openai import OpenAI
import os
import time
from language_tool_python.utils import RateLimitError
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def enhance_typos_with_llm(text):
    prompt = f"""
    Check the following text for spelling, grammar, and punctuation issues in a title insurance document. List each error and the corrected version.

    Text:
    "{text[:1500]}"
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        return f"LLM enhancement unavailable. Error: {str(e)}"

def check_typos_in_chunks(text, tool, chunk_size=5000, max_retries=3):
    """
    Splits the text into smaller chunks and checks each chunk for typos.
    Implements retry logic with exponential backoff for rate limit errors.
    """
    matches = []
    for i in range(0, len(text), chunk_size):
        chunk = text[i:i + chunk_size]
        retries = 0
        while retries < max_retries:
            try:
                matches.extend(tool.check(chunk))
                break  # Exit retry loop on success
            except RateLimitError:
                retries += 1
                if retries < max_retries:
                    delay = 2 ** retries  # Exponential backoff
                    time.sleep(delay)
                else:
                    raise RateLimitError("Max retries exceeded for LanguageTool API.")
    return matches

def check_typos(text, doc_name):
    tool = language_tool_python.LanguageToolPublicAPI('en-US')
    try:
        matches = check_typos_in_chunks(text, tool)
    except RateLimitError as e:
        return [{
            "Document": doc_name,
            "Location": "N/A",
            "Error Type": "API Error",
            "Description": "LanguageTool API rate limit exceeded.",
            "Suggestion": str(e)
        }]
    
    errors = []
    for m in matches:
        line_number = text[:m.offset].count('\n') + 1
        errors.append({
            "Document": doc_name,
            "Location": f"Line {line_number}",
            "Error Type": "Typographical Error",
            "Description": m.message,
            "Suggestion": ", ".join(m.replacements) if m.replacements else "-"
        })

    llm_feedback = enhance_typos_with_llm(text)
    if llm_feedback and "No issues" not in llm_feedback:
        errors.append({
            "Document": doc_name,
            "Location": "LLM Review",
            "Error Type": "Typographical Error (LLM)",
            "Description": "LLM-enhanced review of spelling/grammar:",
            "Suggestion": llm_feedback
        })

    return errors