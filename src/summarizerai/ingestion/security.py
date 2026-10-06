import os
import re
import socket
import ipaddress
from urllib.parse import urlparse
from fastapi import HTTPException
from summarizerai.config import settings

def sanitize_filename(filename: str) -> str:
    """Sanitize uploaded filename to prevent directory traversal and illegal characters."""
    # Strip paths
    clean = os.path.basename(filename)
    # Remove any non-alphanumeric, dot, underscore, dash
    clean = re.sub(r"[^a-zA-Z0-9_.-]", "_", clean)
    # Prevent hidden files
    clean = clean.lstrip(".")
    if not clean:
        clean = "uploaded_file"
    return clean

def validate_file(filename: str, file_size_bytes: int) -> None:
    """Validate file extension and size."""
    ext = os.path.splitext(filename)[1].lower()
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Allowed types: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )
    max_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024
    if file_size_bytes > max_bytes:
        raise HTTPException(
            status_code=400,
            detail=f"File exceeds maximum allowed size of {settings.MAX_FILE_SIZE_MB}MB."
        )

def validate_ssrf_safe_url(url_str: str) -> str:
    """
    Validate that a URL is well-formed, uses http/https, and does not resolve to
    localhost, private IP spaces, link-local addresses, or cloud metadata endpoints.
    """
    try:
        parsed = urlparse(url_str.strip())
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid URL format.")

    if parsed.scheme.lower() not in settings.ALLOWED_SCHEMES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid URL scheme '{parsed.scheme}'. Only http and https are allowed."
        )

    hostname = parsed.hostname
    if not hostname:
        raise HTTPException(status_code=400, detail="URL is missing a valid hostname.")

    # Block localhost names directly
    blocked_hosts = ["localhost", "127.0.0.1", "0.0.0.0", "::1", "metadata.google.internal"]
    if hostname.lower() in blocked_hosts:
        raise HTTPException(status_code=403, detail="Access to local/private network addresses is forbidden.")

    try:
        # Resolve IP to verify it's not a private or link-local address
        addr_info = socket.getaddrinfo(hostname, None)
        for item in addr_info:
            ip_str = item[4][0]
            ip = ipaddress.ip_address(ip_str)
            if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_multicast:
                raise HTTPException(
                    status_code=403,
                    detail="Access to private or restricted network addresses is forbidden."
                )
    except socket.gaierror:
        raise HTTPException(status_code=400, detail=f"Could not resolve host: {hostname}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"SSRF validation error: {str(e)}")

    return url_str.strip()
