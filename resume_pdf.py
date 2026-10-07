"""Extract selectable resume text from a PDF uploaded in Streamlit."""
from io import BytesIO

from pypdf import PdfReader


def extract_pdf_text(data: bytes) -> str:
    try:
        reader = PdfReader(BytesIO(data))
        return "\n".join(page.extract_text() or "" for page in reader.pages).strip()
    except Exception:
        raise ValueError("Could not read this PDF. Please paste your resume text instead.") from None
