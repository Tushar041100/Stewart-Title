import streamlit as st
from document_parser import parse_documents
from error_detectors.typo_checker import check_typos
from error_detectors.name_checker import check_names
from error_detectors.date_checker import check_dates
from error_detectors.domain_checker import check_domain_rules
from error_detectors.missing_info_checker import check_missing_info
from report_generator import generate_report
import os

output_directory = "C:/Tushar/Stewart Title/reports/"
os.makedirs(output_directory, exist_ok=True)

st.set_page_config(page_title="Insurance Document Validator")
st.title("Insurance Document Validator")
st.markdown("Upload insurance/title documents (PDF, DOCX, XLSX). Max 20MB each.")
 
uploaded_files = st.file_uploader("Choose files", type=["pdf", "docx", "xlsx"], accept_multiple_files=True)
 
if uploaded_files:
    if st.button("Run Analysis"):
        with st.spinner("Processing documents..."):
            error_records = []
 
            for file in uploaded_files:
                file_path = os.path.join(output_directory, file.name)
                with open(file_path, "wb") as f:
                    f.write(file.read())
 
                doc_text, doc_meta = parse_documents(file_path)
 
                errors = []
                errors += check_typos(doc_text, file.name)
                errors += check_names(doc_text, file.name)
                errors += check_dates(doc_text, file.name)
                errors += check_domain_rules(doc_text, file.name)
                errors += check_missing_info(doc_text, file.name)
 
                error_records.extend(errors)
 
            output_file = os.path.join(output_directory, "error_report.xlsx")
            output_file = os.path.normpath(output_file)  # Normalize the path
            generate_report(error_records, output_file)
 
        st.success("Analysis complete. Download the report below:")
        with open(output_file, "rb") as f:
            st.download_button("Download Excel Report", data=f, file_name="error_report.xlsx")
 
        st.info(f"Report saved locally at: {output_file}")