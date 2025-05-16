import openai
import os
 
openai.api_key = os.getenv("OPENAI_API_KEY")
 
REQUIRED_SECTIONS = [
    "Policy Start Date", "Schedule A", "Legal Description", "Proposed Insured"
]
 
def check_missing_info(text, doc_name):
    errors = []
 
    # Rule-based check
    for section in REQUIRED_SECTIONS:
        if section.lower() not in text.lower():
            errors.append({
                "Document": doc_name,
                "Location": "-",
                "Error Type": "Missing Information",
                "Description": f"Required section or field missing: {section}",
                "Suggestion": "Please add this information"
            })
 
    # LLM-enhanced check
    llm_feedback = query_llm_for_missing_fields(text)
    if llm_feedback and "No issues" not in llm_feedback:
        errors.append({
            "Document": doc_name,
            "Location": "LLM Review",
            "Error Type": "Missing Information (LLM)",
            "Description": "Potential missing sections detected by LLM",
            "Suggestion": llm_feedback
        })
 
    return errors
 
def query_llm_for_missing_fields(text_snippet):
    prompt = f"""
    You are a title insurance compliance assistant. Review the following document text and list any important required fields or sections that appear to be missing.
    Use insurance-specific knowledge. If nothing is missing, respond with 'No issues'.
 
    Text:
    \"\"\"{text_snippet[:3000]}\"\"\"
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        return response["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"LLM error: {e}"
 