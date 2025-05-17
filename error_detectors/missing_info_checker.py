from utils.groq_client import query_groq
  
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
    llm_feedback = query_llm_for_missing_fields_in_chunks(text)
    if llm_feedback and "No issues" not in llm_feedback:
        errors.append({
            "Document": doc_name,
            "Location": "LLM Review",
            "Error Type": "Missing Information (LLM)",
            "Description": "Potential missing sections detected by LLM",
            "Suggestion": llm_feedback
        })
 
    return errors
 
def query_llm_for_missing_fields_in_chunks(text):
    chunk_size = 1000
    chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]
    feedback = []

    for chunk in chunks:
        prompt = f"""
        You are a title insurance compliance assistant. Review the following document text and list any important required fields or sections that appear to be missing.
        Use insurance-specific knowledge. If nothing is missing, respond with 'No issues'.

        Text:
        \"\"\"{chunk}\"\"\"
        """
        try:
            response = query_groq(prompt)
            print("LLM Response:", response)  # Debugging
            if response and "No issues" not in response:
                feedback.append(response)
        except Exception as e:
            feedback.append(f"LLM error: {e}")

    # Combine feedback from all chunks
    return " | ".join(feedback) if feedback else "No issues"
 