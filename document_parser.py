import textract
import docx
import os
import pandas as pd
from PyPDF2 import PdfReader
from utils.groq_client import query_groq
 
def summarize_content(text, chunk_size=1000, overlap=100):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start += chunk_size - overlap

    # Summarize each chunk
    summaries = []
    for idx, chunk in enumerate(chunks):
        print(f"Summarizing chunk {idx + 1}/{len(chunks)}...")

        prompt = f"""
        Summarize the following insurance document text in one paragraph for context-aware processing:
    
        """
        prompt += chunk  # limit tokens for safety
    
        try:
            summary = query_groq(prompt)
            summaries.append(summary)
        except Exception:
            print(f"Error summarizing chunk {idx + 1}: {e}")
            summaries.append("")
    combined_summary_text = "\n".join(summaries)
    final_prompt = f"Combine the following summaries into a cohesive summary:\n\n{combined_summary_text}"
    try:
        final_summary = query_groq(final_prompt)
    except Exception as e:
        print(f"Error generating final summary: {e}")
        final_summary = combined_summary_text  # Fallback to combined summaries

    return final_summary
 
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