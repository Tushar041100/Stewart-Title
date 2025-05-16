import pandas as pd
 
def generate_report(errors, output_path):
    if errors:
        df = pd.DataFrame(errors)
        df.to_excel(output_path, index=False)
    else:
        df = pd.DataFrame([{"Document": "-", "Location": "-", "Error Type": "None", "Description": "No issues found.", "Suggestion": "-"}])
        df.to_excel(output_path, index=False)