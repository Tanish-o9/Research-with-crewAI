import os
from pathlib import Path
from typing import List, Optional

try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extracts text content from a PDF file using pypdf."""
    if not PdfReader:
        return "[PDF reader library 'pypdf' not installed]"

    try:
        reader = PdfReader(pdf_path)
        extracted = []
        for i, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            if text.strip():
                extracted.append(f"--- Page {i + 1} ---\n{text.strip()}")
        return "\n\n".join(extracted)
    except Exception as e:
        return f"[Error reading PDF {pdf_path}: {str(e)}]"


def load_knowledge_documents(knowledge_dir: str = "knowledge") -> str:
    """
    Scans the knowledge directory for .txt, .md, and .pdf files,
    extracts their contents, and formats them as background knowledge context.
    """
    path = Path(knowledge_dir)
    if not path.exists():
        return ""

    documents = []
    supported_files = list(path.glob("*.txt")) + list(path.glob("*.md")) + list(path.glob("*.pdf"))

    for file_path in supported_files:
        try:
            if file_path.suffix.lower() == ".pdf":
                content = extract_text_from_pdf(str(file_path))
            else:
                with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                    content = f.read().strip()

            if content:
                # Truncate per document if extremely long
                words = content.split()
                if len(words) > 3000:
                    content = " ".join(words[:3000]) + "\n[...Document truncated for length...]"
                documents.append(f"### Document: {file_path.name}\n{content}")

        except Exception as e:
            print(f"Failed to process knowledge document {file_path}: {e}")

    if not documents:
        return ""

    return "\n\n---\n\n".join(documents)


def save_uploaded_knowledge_file(uploaded_file, target_dir: str = "knowledge") -> str:
    """
    Saves an uploaded file (from Streamlit) into the knowledge directory.
    Returns the saved file path.
    """
    os.makedirs(target_dir, exist_ok=True)
    save_path = os.path.join(target_dir, uploaded_file.name)
    with open(save_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return save_path
