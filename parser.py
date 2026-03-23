import pandas as pd
import PyPDF2
import os

def parse_txt(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

def parse_pdf(file_path: str) -> str:
    text = ""
    try:
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        print(f"Error parsing PDF: {e}")
    return text

def parse_csv(file_path: str) -> pd.DataFrame:
    try:
        df = pd.read_csv(file_path)
        return df
    except Exception as e:
        print(f"Error parsing CSV: {e}")
        return pd.DataFrame()

def parse_excel(file_path: str) -> pd.DataFrame:
    try:
        df = pd.read_excel(file_path)
        return df
    except Exception as e:
        print(f"Error parsing Excel: {e}")
        return pd.DataFrame()

def parse_python_file(file_path: str) -> str:
    # Later this can be expanded to use AST for deeper structural parsing
    return parse_txt(file_path)

def process_file(file_path: str, filename: str):
    ext = os.path.splitext(filename)[1].lower()
    if ext == ".txt":
        return parse_txt(file_path), "text"
    elif ext == ".pdf":
        return parse_pdf(file_path), "text"
    elif ext == ".csv":
        return parse_csv(file_path), "dataframe"
    elif ext in [".xls", ".xlsx"]:
        return parse_excel(file_path), "dataframe"
    elif ext == ".py":
        return parse_python_file(file_path), "code"
    else:
        raise ValueError(f"Unsupported file type: {ext}")
