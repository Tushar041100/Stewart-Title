import re
from dateutil.parser import parse as parse_date, ParserError
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
 
def check_dates(text, doc_name):
    date_pattern = re.compile(r"\b\d{1,4}[-/\.\s]\d{1,2}[-/\.\s]\d{1,4}\b")
    dates = date_pattern.findall(text)
    parsed_dates = []
    errors = []
 
    for date_str in dates:
        try:
            parsed = parse_date(date_str, dayfirst=False, fuzzy=True)
            parsed_dates.append(parsed)
        except ParserError:
            errors.append({
                "Document": doc_name,
                "Location": "-",
                "Error Type": "Date Inconsistency",
                "Description": f"Unparsable or unusual date: {date_str}",
                "Suggestion": "Use YYYY-MM-DD format"
            })
            
    print(parsed_dates) ##Note

    for i in range(len(parsed_dates) - 1):
        if parsed_dates[i] > parsed_dates[i + 1]:
            errors.append({
                "Document": doc_name,
                "Location": "-",
                "Error Type": "Date Sequence Error",
                "Description": f"{parsed_dates[i]} appears after {parsed_dates[i + 1]}",
                "Suggestion": "Verify the timeline"
            })
 
    if parsed_dates:
        logic_eval = evaluate_date_logic_with_llm(dates)
        if "issue" in logic_eval.lower():
            errors.append({
                "Document": doc_name,
                "Location": "LLM Insight",
                "Error Type": "Date Inconsistency (LLM)",
                "Description": "LLM date sequence review",
                "Suggestion": logic_eval
            })
 
    return errors
 
def evaluate_date_logic_with_llm(date_list):
    prompt = f"Given these dates from an insurance document, do you see any logical inconsistencies?\n{date_list}"
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        return response['choices'][0]['message']['content']
    except Exception:
        return "Could not evaluate date logic."