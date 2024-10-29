import PyPDF2
from dotenv import load_dotenv
import os

load_dotenv()


def parse_file(file):
    """
    Extract chapter names from a PDF file.

    Parameters:
        file: Uploaded file object in Streamlit.

    Returns:
        List of chapter names found in the file.
    """
    chapter_titles = []

    if file.name.endswith(".pdf"):
        try:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:

                text += page.extract_text() or ""


            lines = text.splitlines()
            for line in lines:

                if line.strip() and line[0].isdigit() and "." in line:
                    chapter_titles.append(line.strip())

            if not chapter_titles:
                raise Exception("No chapter titles found in the PDF file.")

            return chapter_titles

        except Exception as e:
            raise Exception(f"Error reading the PDF file: {e}")
    else:
        raise Exception("Unsupported File Format. Only PDF files are supported.")
