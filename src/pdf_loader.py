from pathlib import Path
from typing import List
from pypdf import PdfReader


def load_pdf_text(path: str | Path) -> str:
    path = Path(path)
    reader = PdfReader(str(path))
    texts: List[str] = []
    for page in reader.pages:
        texts.append(page.extract_text() or "")
    return "\n\n".join(texts)
