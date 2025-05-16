import os
import textract
import docx
import pandas as pd
from PyPDF2 import PdfReader
import openai
 
openai.api_key = os.getenv("OPENAI_API_KEY")
 
def summarize_content(text):
    prompt = f"""
    Summarize the following insurance document text in one paragraph for context-aware processing:
 
    """
    prompt += text[:3000]  # limit tokens for safety
 
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
    except Exception:
        return "Summary unavailable due to API error."
 
def parse_documents(file_path):
    text = ""
    meta = {}
    ext = os.path.splitext(file_path)[-1].lower()
 
    if ext == ".pdf":
        reader = PdfReader(file_path)
        text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
    elif ext == ".docx":
        doc = docx.Document(file_path)
        text = "\n".join([para.text for para in doc.paragraphs])
    elif ext == ".xlsx":
        df = pd.read_excel(file_path, sheet_name=None)
        text = ""
        for sheet, frame in df.items():
            text += f"\nSheet: {sheet}\n" + frame.fillna("").astype(str).apply(" ".join, axis=1).str.cat(sep="\n")
    else:
        text = textract.process(file_path).decode("utf-8")

    meta["summary"] = summarize_content(text)
    return text.strip(), meta