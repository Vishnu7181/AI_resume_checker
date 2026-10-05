import io


def extract_text(filename: str, content: bytes) -> str:
    name = (filename or "").lower()

    if name.endswith(".pdf"):
        return _extract_pdf(content)
    elif name.endswith(".docx"):
        return _extract_docx(content)
    elif name.endswith(".txt"):
        return content.decode("utf-8", errors="ignore")

    raise ValueError(f"Unsupported file type: {name}. Use PDF, DOCX, or TXT.")


def _extract_pdf(content: bytes) -> str:
    # Sanity check: a real PDF always starts with %PDF
    if not content.startswith(b"%PDF"):
        if content[:2] == b"PK":
            raise ValueError(
                "This file is actually a DOCX/ZIP renamed to .pdf. "
                "Please export a real PDF (File → Save As / Export → PDF)."
            )
        raise ValueError(
            "This file is not a valid PDF — it may be corrupted or a renamed file. "
            "Re-export it as PDF and try again."
        )

    # Attempt 1: pdfplumber
    try:
        import pdfplumber
        with pdfplumber.open(io.BytesIO(content)) as pdf:
            text = "\n".join(page.extract_text() or "" for page in pdf.pages)
        if text.strip():
            return text
    except Exception:
        pass  # fall through to pypdf

    # Attempt 2: pypdf fallback
    try:
        from pypdf import PdfReader
        reader = PdfReader(io.BytesIO(content))
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
        if text.strip():
            return text
    except Exception:
        pass

    
        # Attempt 3: OCR fallback for scanned/image PDFs
    try:
        from pdf2image import convert_from_bytes
        import pytesseract

        images = convert_from_bytes(
            content, dpi=200,
            poppler_path=r"C:\poppler\Library\bin"  # adjust to your poppler path
        )
        text = "\n".join(pytesseract.image_to_string(img) for img in images)
        if text.strip():
            return text
    except Exception as e:
        pass

    raise ValueError(
        "Could not extract text from this PDF. It appears to be scanned/image-only "
        "and OCR failed. Please upload a text-based PDF exported from Word/Docs/Canva."
    )


def _extract_docx(content: bytes) -> str:
    from docx import Document
    doc = Document(io.BytesIO(content))
    return "\n".join(p.text for p in doc.paragraphs if p.text.strip())
MAX_SIZE = 5 * 1024 * 1024  # 5 MB
ALLOWED_EXTENSIONS = (".pdf", ".docx", ".txt")


def validate_file(filename: str, content: bytes) -> None:
    """Raises ValueError if the file is invalid. Returns None if OK."""
    name = (filename or "").lower()

    if not name.endswith(ALLOWED_EXTENSIONS):
        raise ValueError("Unsupported file type. Please upload a PDF, DOCX, or TXT file.")
    if len(content) == 0:
        raise ValueError("The uploaded file is empty.")
    if len(content) > MAX_SIZE:
        raise ValueError("File too large. Maximum size is 5 MB.")
