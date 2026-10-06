import re
from urllib.parse import urlparse

def detect_url_source_type(url: str) -> str:
    """Detect if a URL is YouTube, Research Paper (arXiv), or standard Website."""
    url_lower = url.lower().strip()
    parsed = urlparse(url_lower)
    domain = parsed.netloc

    # YouTube detection
    if "youtube.com" in domain or "youtu.be" in domain:
        return "youtube"

    # Research Paper detection
    if "arxiv.org" in domain or "biorxiv.org" in domain or "medrxiv.org" in domain:
        return "research_paper"
    if "semanticscholar.org" in domain or "doi.org" in domain:
        return "research_paper"
    if url_lower.endswith(".pdf") and any(k in url_lower for k in ["paper", "article", "thesis", "proceedings", "conference"]):
        return "research_paper"

    return "website"

def detect_file_source_type(filename: str) -> str:
    """Detect source type from file extension."""
    filename_lower = filename.lower()
    if filename_lower.endswith(".pdf"):
        return "pdf"
    elif filename_lower.endswith((".txt", ".md", ".text")):
        return "txt"
    return "txt"
