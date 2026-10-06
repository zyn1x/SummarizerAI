import os
import fitz  # PyMuPDF
from typing import List, Dict, Any
from summarizerai.processing.canonical import CanonicalDocument, CanonicalChunk
from summarizerai.processing.normalizer import normalize_text
from summarizerai.chunking.structure_chunker import chunk_text_with_metadata

class PDFExtractionError(Exception):
    pass

def extract_pdf_content(file_path: str, original_filename: str) -> CanonicalDocument:
    """
    Extract text from PDF using PyMuPDF with per-page tracking and OCR fallback readiness.
    Preserves exact 1-indexed page numbers.
    """
    if not os.path.exists(file_path):
        raise PDFExtractionError(f"PDF file not found at: {file_path}")

    try:
        doc = fitz.open(file_path)
    except Exception as e:
        raise PDFExtractionError(f"Failed to open PDF (file may be corrupted or invalid): {e}")

    if doc.is_encrypted:
        raise PDFExtractionError("PDF is password-protected. Please provide an unencrypted PDF.")

    page_count = len(doc)
    if page_count == 0:
        raise PDFExtractionError("PDF document contains no pages.")

    all_chunks: List[CanonicalChunk] = []
    full_text_parts: List[str] = []
    chunk_index = 0
    scanned_pages = []

    # Document title from metadata or filename
    pdf_meta = doc.metadata or {}
    title = pdf_meta.get("title") or os.path.splitext(original_filename)[0].replace("_", " ").title()

    for page_idx in range(page_count):
        page = doc.load_page(page_idx)
        page_num = page_idx + 1  # 1-indexed page number
        
        # PyMuPDF text extraction
        text = page.get_text("text") or ""
        # pyrefly: ignore [bad-argument-type]
        cleaned = normalize_text(text)

        # Check if page looks like a scanned image (very few characters)
        if len(cleaned.strip()) < 35:
            # Check for OCR fallback
            try:
                # pyrefly: ignore [missing-import]
                import pytesseract
                # pyrefly: ignore [missing-import]
                from PIL import Image
                import io
                pix = page.get_pixmap(dpi=150)
                img = Image.open(io.BytesIO(pix.tobytes("png")))
                ocr_text = pytesseract.image_to_string(img)
                if len(ocr_text.strip()) > len(cleaned.strip()):
                    cleaned = normalize_text(ocr_text)
            except Exception:
                # OCR not available or failed; mark as low-text page
                scanned_pages.append(page_num)

        if cleaned.strip():
            full_text_parts.append(f"--- [Page {page_num}] ---\n" + cleaned)
            # Create structure-aware chunks tagged with this page_number
            page_chunks = chunk_text_with_metadata(
                text=cleaned,
                target_words=250,
                overlap_words=35,
                page_number=page_num,
                section_heading=f"Page {page_num}",
                start_chunk_idx=chunk_index
            )
            all_chunks.extend(page_chunks)
            chunk_index += len(page_chunks)

    doc.close()

    raw_text = "\n\n".join(full_text_parts)
    if not raw_text.strip():
        raise PDFExtractionError("Could not extract readable text from PDF. The document may be completely blank or an unsupported scan.")

    return CanonicalDocument(
        title=title,
        source_type="pdf",
        original_filename=original_filename,
        raw_text=raw_text,
        file_size_bytes=os.path.getsize(file_path),
        chunks=all_chunks,
        metadata={
            "page_count": page_count,
            "scanned_pages": scanned_pages,
            "author": pdf_meta.get("author", ""),
            "creator": pdf_meta.get("creator", ""),
        }
    )
