import re
import os
import openai
 
openai.api_key = os.getenv("OPENAI_API_KEY")
 
def query_llm_for_terminology(text_snippet):
    prompt = f"""
    You are an expert in title insurance compliance. Identify any improper or non-standard use of insurance terminology in the following text.
    Suggest corrections if necessary. If everything looks fine, respond with 'No issues'.
 
    Text:
    "{text_snippet}"
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )
        return response["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"LLM check failed: {e}"
 
def check_domain_rules(text, doc_name):
    errors = []
 
    if match := re.search(r"Policy(?:\s|#)?Number\s*[:\-]?\s*(\w+)", text, re.IGNORECASE):
        number = match.group(1)
        if not re.match(r"^[A-Z]{3}\d{6}$", number):
            errors.append({
                "Document": doc_name,
                "Location": "-",
                "Error Type": "Policy Number Error",
                "Description": f"Unusual policy number format: {number}",
                "Suggestion": "Expected format: ABC123456"
            })
 
    if match := re.search(r"Proposed Amount of Insurance.*?\$([\d,]+)\.?", text, re.IGNORECASE):
        amount = int(match.group(1).replace(",", ""))
        if amount > 10000000:
            errors.append({
                "Document": doc_name,
                "Location": "-",
                "Error Type": "Coverage Amount Error",
                "Description": f"Very high coverage amount: ${amount}",
                "Suggestion": "Confirm if this is realistic"
            })
 
    if "insured person" in text.lower():
        llm_feedback = query_llm_for_terminology("insured person")
        errors.append({
            "Document": doc_name,
            "Location": "-",
            "Error Type": "Terminology Error (LLM)",
            "Description": "Non-standard term detected: 'insured person'",
            "Suggestion": llm_feedback
        })
 
    return errors