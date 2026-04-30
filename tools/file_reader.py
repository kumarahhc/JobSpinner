import os
import pdfplumber
import logging
from config import CV_FOLDER

logging.basicConfig(level=logging.INFO)

_BINARY_SAMPLE_BYTES = 8192
_MAX_NON_PRINTABLE_RATIO = 0.10


def _assert_allowed_path(file_path: str) -> str:
    """
    Verify that the file is inside CV_FOLDER.
    Returns the resolved path, or raises PermissionError.
    """
    resolved = os.path.realpath(os.path.abspath(file_path))
    allowed  = os.path.realpath(CV_FOLDER)
    if not resolved.startswith(allowed + os.sep) and resolved != allowed:
        raise PermissionError(
            f"Access denied: '{file_path}' is outside the allowed folder '{CV_FOLDER}'."
        )
    return resolved


def _is_binary(file_path: str) -> bool:
    """
    Return True if the file looks like binary (non-text) content.
    """
    try:
        with open(file_path, "rb") as f:
            sample = f.read(_BINARY_SAMPLE_BYTES)
        if b"\x00" in sample:
            return True
        non_printable = sum(
            1 for b in sample if b < 9 or (13 < b < 32) or b == 127
        )
        return (non_printable / max(len(sample), 1)) > _MAX_NON_PRINTABLE_RATIO
    except OSError:
        return False


def read_cv_pdf(file_path: str) -> str:
    """
    Tool: Read CV content from a PDF or TEXT file and return the extracted text.
    Only files inside the configured CV_FOLDER are accessible.
    Binary files are rejected even when they carry a .txt extension.

    Args:
        file_path (str): Path to the CV file (PDF or TXT).
    Returns:
        str: Extracted text content.
    """
    logging.info(f"Reading CV from file: {file_path}")

    resolved = _assert_allowed_path(file_path)

    if not os.path.isfile(resolved):
        raise FileNotFoundError(f"File not found: {file_path}")

    ext = os.path.splitext(resolved)[1].lower()
    if ext not in (".pdf", ".txt"):
        raise ValueError(
            f"Unsupported file type: '{ext}'. Only PDF and TXT files are accepted."
        )

    if ext == ".txt":
        if _is_binary(resolved):
            raise ValueError(
                f"File '{file_path}' appears to contain binary data and cannot be read as text."
            )
        try:
            with open(resolved, "r", encoding="utf-8") as f:
                return f.read().strip()
        except Exception as e:
            logging.error(f"Error reading text file: {e}")
            return ""

    # PDF — 
    try:
        extracted_pages = []
        with pdfplumber.open(resolved) as pdf:
            total_pages = len(pdf.pages)
            logging.info(f"Total pages in PDF: {total_pages}")
            for i, page in enumerate(pdf.pages):
                logging.info(f"Extracting text from page {i + 1}/{total_pages}")
                text = page.extract_text()
                if text:
                    extracted_pages.append(text.strip())
        return "\n".join(extracted_pages)
    except Exception as e:
        logging.error(f"Error reading PDF file: {e}")
        return ""
