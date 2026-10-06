import pytest
from summarizerai.chunking.structure_chunker import chunk_text_with_metadata
from summarizerai.processing.normalizer import normalize_text, detect_sections
from summarizerai.ingestion.detector import detect_url_source_type, detect_file_source_type
from summarizerai.ingestion.security import validate_ssrf_safe_url, sanitize_filename
from fastapi import HTTPException

def test_detect_source_types():
    assert detect_url_source_type("https://www.youtube.com/watch?v=dQw4w9WgXcQ") == "youtube"
    assert detect_url_source_type("https://youtu.be/dQw4w9WgXcQ") == "youtube"
    assert detect_url_source_type("https://arxiv.org/abs/1706.03762") == "research_paper"
    assert detect_url_source_type("https://en.wikipedia.org/wiki/Artificial_intelligence") == "website"
    assert detect_file_source_type("research_paper.pdf") == "pdf"
    assert detect_file_source_type("notes.txt") == "txt"

def test_normalize_and_detect_sections():
    raw = "Title: Deep Learning\n\n1. Introduction\nDeep learning is a subset of machine learning.\n\n2. Methodology\nWe train neural networks on large datasets."
    cleaned = normalize_text(raw)
    sections = detect_sections(cleaned)
    assert len(sections) >= 2
    headings = [h for h, _ in sections]
    assert any("Introduction" in h for h in headings)
    assert any("Methodology" in h for h in headings)

def test_chunk_text_with_metadata_preservation():
    sample_text = (
        "Artificial intelligence is transforming society. Machine learning models process vast data. "
        "Deep neural networks discover intricate representations. Reinforcement learning optimizes policy. "
        "Transformer architectures revolutionized natural language processing. Attention is all you need."
    )
    chunks = chunk_text_with_metadata(
        text=sample_text,
        target_words=15,
        overlap_words=5,
        page_number=3,
        section_heading="Architectures",
        timestamp_formatted="02:30",
        timestamp_start=150.0,
        timestamp_end=170.0
    )
    assert len(chunks) >= 1
    for chunk in chunks:
        assert chunk.page_number == 3
        assert chunk.section_heading == "Architectures"
        assert chunk.timestamp_formatted == "02:30"
        assert chunk.to_citation_label() == "[p. 3]"

def test_ssrf_protection():
    # Valid external URLs
    assert validate_ssrf_safe_url("https://example.com/article") == "https://example.com/article"

    # Blocked local IPs and non-http schemes
    with pytest.raises(HTTPException):
        validate_ssrf_safe_url("http://localhost:8000/secret")

    with pytest.raises(HTTPException):
        validate_ssrf_safe_url("http://127.0.0.1:8000/api")

    with pytest.raises(HTTPException):
        validate_ssrf_safe_url("file:///etc/passwd")

def test_sanitize_filename():
    assert sanitize_filename("../../etc/passwd.pdf") == "passwd.pdf"
    assert sanitize_filename("my file (1).txt") == "my_file__1_.txt"
