import re
from io import BytesIO
from typing import Optional
import PyPDF2

MAX_PAGES = 60  # protect from huge uploads

def extract_pdf_text(file_bytes: BytesIO) -> str:
    """
    Safe-ish PDF text extraction:
    - caps pages
    - ignores extraction failures per page
    """
    reader = PyPDF2.PdfReader(file_bytes)
    text_chunks: list[str] = []
    for i, page in enumerate(reader.pages[:MAX_PAGES]):
        try:
            text_chunks.append(page.extract_text() or "")
        except Exception:
            continue
    text = "\n".join(text_chunks)
    text = re.sub(r"\s+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()
