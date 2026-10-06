import re
import os
import httpx
import xml.etree.ElementTree as ET
from urllib.parse import urlparse
from typing import Optional, Dict, Any, List
from summarizerai.processing.canonical import CanonicalDocument, CanonicalChunk
from summarizerai.ingestion.pdf_extractor import extract_pdf_content
from summarizerai.ingestion.security import validate_ssrf_safe_url
from summarizerai.config import settings

class ResearchPaperExtractionError(Exception):
    pass

def extract_arxiv_id(url_or_id: str) -> Optional[str]:
    """Extract arXiv ID from URL or raw ID string."""
    clean = url_or_id.strip()
    # Match arxiv.org/abs/2301.12345 or arxiv.org/pdf/2301.12345.pdf
    m = re.search(r"arxiv\.org/(?:abs|pdf)/([0-9]+\.[0-9]+(?:v[0-9]+)?|[a-z\-]+/[0-9]+)", clean, re.IGNORECASE)
    if m:
        return m.group(1).replace(".pdf", "")
    # Match standalone id pattern e.g. 2301.12345
    m2 = re.match(r"^([0-9]{4}\.[0-9]{4,5}(?:v[0-9]+)?)$", clean)
    if m2:
        return m2.group(1)
    return None

async def fetch_arxiv_metadata(arxiv_id: str) -> Dict[str, Any]:
    """Query arXiv API for paper metadata."""
    api_url = f"http://export.arxiv.org/api/query?id_list={arxiv_id}"
    try:
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.get(api_url)
            if resp.status_code != 200:
                return {}
            
            root = ET.fromstring(resp.text)
            ns = {"atom": "http://www.w3.org/2005/Atom"}
            entry = root.find("atom:entry", ns)
            if entry is None:
                return {}
            
            title = entry.find("atom:title", ns)
            summary = entry.find("atom:summary", ns)
            published = entry.find("atom:published", ns)
            # pyrefly: ignore [missing-attribute]
            authors = [a.find("atom:name", ns).text for a in entry.findall("atom:author", ns) if a.find("atom:name", ns) is not None]
            
            return {
                # pyrefly: ignore [missing-attribute]
                "title": title.text.strip().replace("\n", " ") if title is not None else "",
                # pyrefly: ignore [missing-attribute]
                "abstract": summary.text.strip().replace("\n", " ") if summary is not None else "",
                "published": published.text if published is not None else "",
                "authors": authors,
                "arxiv_id": arxiv_id
            }
    except Exception:
        return {}

async def extract_research_paper(url: str) -> CanonicalDocument:
    """
    Extract content from arXiv or scientific paper URLs.
    Downloads PDF if available, parses metadata, and structures paper sections.
    """
    validate_ssrf_safe_url(url)
    arxiv_id = extract_arxiv_id(url)
    pdf_url = url

    arxiv_meta = {}
    if arxiv_id:
        arxiv_meta = await fetch_arxiv_metadata(arxiv_id)
        pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"

    # Download PDF to temp file
    temp_pdf_path = settings.TEMP_DIR / f"paper_{arxiv_id or 'doc'}_{os.getpid()}.pdf"

    try:
        async with httpx.AsyncClient(timeout=45, follow_redirects=True) as client:
            resp = await client.get(pdf_url)
            if resp.status_code != 200:
                raise ResearchPaperExtractionError(f"Failed to download research paper PDF: HTTP {resp.status_code}")
            with open(temp_pdf_path, "wb") as f:
                f.write(resp.content)

        # Use PyMuPDF extractor on the downloaded PDF
        canon_doc = extract_pdf_content(str(temp_pdf_path), original_filename=f"{arxiv_id or 'research_paper'}.pdf")
        
        # Override title & enrich metadata if arXiv API metadata is present
        if arxiv_meta.get("title"):
            canon_doc.title = arxiv_meta["title"]
        canon_doc.source_type = "research_paper"
        canon_doc.source_url = url
        canon_doc.metadata.update(arxiv_meta)

        return canon_doc
    finally:
        if os.path.exists(temp_pdf_path):
            try:
                os.remove(temp_pdf_path)
            except OSError:
                pass
