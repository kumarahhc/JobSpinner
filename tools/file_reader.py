import os
import pdfplumber
import logging

logging.basicConfig(level=logging.INFO)

def read_cv_pdf(file_path:str) -> str:
    """
    Tool: Read CV content from a PDF or TEXT file and return the extracted text.
    Args:        file_path (str): The path to the CV file (PDF or TEXT).
    Returns:        str: The extracted text content of the CV."""
    logging.info(f"Reading CV from file: {file_path}")
    
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    ext=os.path.splitext(file_path)[1].lower()
    if ext == ".txt":
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content= f.read().strip()
        except Exception as e:
            logging.error(f"Error reading text file: {e}")
            return ""
        return content
    elif ext == ".pdf":
        try:
            extracted_pages = []
            with pdfplumber.open(file_path) as pdf:
                total_pages = len(pdf.pages)
                logging.info(f"Total pages in PDF: {total_pages}")
                for i, page in enumerate(pdf.pages):
                    logging.info(f"Extracting text from page {i+1}/{total_pages}")
                    text = page.extract_text()
                    if text:
                        extracted_pages.append(text.strip())
            return "\n".join(extracted_pages)
        
        except Exception as e:
            logging.error(f"Error reading PDF file: {e}")
            return ""
    else:
        raise ValueError(f"Unsupported file type: {ext}. Only PDF and TEXT files are supported.")
    