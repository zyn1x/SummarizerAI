import httpx
import trafilatura
from bs4 import BeautifulSoup
from typing import List, Tuple
from summarizerai.processing.canonical import CanonicalDocument, CanonicalChunk
from summarizerai.processing.normalizer import normalize_text
from summarizerai.chunking.structure_chunker import chunk_text_with_metadata
from summarizerai.ingestion.security import validate_ssrf_safe_url
from summarizerai.config import settings

class WebExtractionError(Exception):
    pass

async def extract_web_content(url: str) -> CanonicalDocument:
    """
    Extract web content using Trafilatura with BeautifulSoup fallback
    preserving section titles and structure.
    """
    safe_url = validate_ssrf_safe_url(url)

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 SummarizerAI/1.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }

    try:
        async with httpx.AsyncClient(timeout=settings.REQUEST_TIMEOUT_SECONDS, follow_redirects=True) as client:
            resp = await client.get(safe_url, headers=headers)
            if resp.status_code >= 400:
                raise WebExtractionError(f"HTTP error {resp.status_code} when fetching website.")
            html_content = resp.text
    except httpx.RequestError as e:
        raise WebExtractionError(f"Failed to connect to website: {e}")

    # Extract clean text with trafilatura
    extracted_text = trafilatura.extract(
        html_content,
        include_comments=False,
        include_tables=True,
        no_fallback=False,
        output_format="txt"
    )

    soup = BeautifulSoup(html_content, "html.parser")
    page_title = ""
    if soup.title and soup.title.string:
        page_title = soup.title.string.strip()
    elif soup.find("h1"):
        # pyrefly: ignore [missing-attribute]
        page_title = soup.find("h1").get_text().strip()
    else:
        page_title = safe_url

    # Fallback to BeautifulSoup if trafilatura missed main content
    if not extracted_text or len(extracted_text.strip()) < 100:
        # Strip script and style
        for tag in soup(["script", "style", "nav", "footer", "header", "noscript"]):
            tag.decompose()
        extracted_text = soup.get_text(separator="\n\n")

    cleaned = normalize_text(extracted_text)
    if not cleaned.strip():
        raise WebExtractionError("Website content could not be extracted or is empty.")

    # Extract headings and sections
    sections: List[Tuple[str, str]] = []
    current_heading = "Overview"
    current_paragraphs: List[str] = []

    # Parse structural blocks from body
    content_root = soup.find("article") or soup.find("main") or soup.body
    if content_root:
        for elem in content_root.find_all(["h1", "h2", "h3", "p"]):
            text = elem.get_text().strip()
            if not text:
                continue
            if elem.name in ["h1", "h2", "h3"]:
                if current_paragraphs:
                    sec_content = "\n\n".join(current_paragraphs).strip()
                    if sec_content:
                        sections.append((current_heading, sec_content))
                    current_paragraphs = []
                current_heading = text[:80]
            else:
                current_paragraphs.append(text)
        
        if current_paragraphs:
            sec_content = "\n\n".join(current_paragraphs).strip()
            if sec_content:
                sections.append((current_heading, sec_content))

    if not sections:
        sections = [("Overview", cleaned)]

    all_chunks: List[CanonicalChunk] = []
    chunk_index = 0

    for heading, text_block in sections:
        sec_chunks = chunk_text_with_metadata(
            text=text_block,
            target_words=250,
            overlap_words=35,
            section_heading=heading,
            start_chunk_idx=chunk_index
        )
        all_chunks.extend(sec_chunks)
        chunk_index += len(sec_chunks)

    return CanonicalDocument(
        title=page_title,
        source_type="website",
        source_url=safe_url,
        raw_text=cleaned,
        chunks=all_chunks,
        metadata={
            "section_count": len(sections),
            "status_code": resp.status_code,
        }
    )
