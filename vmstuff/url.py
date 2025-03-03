"""URL manipulation functions."""

from urllib.parse import urlparse


def get_base_url(url: str, /, *, include_path: bool = False) -> str:
    """Extract the base URL from a given URL.
    
    Args:
        url: The URL to process.
        include_path: Whether to include the path in the base URL. Defaults to False.
            When True, includes everything up to but not including query parameters or fragments.
    
    Returns:
        The base URL (scheme + netloc, and optionally path).
        
    Raises:
        ValueError: If the URL is invalid (e.g., missing scheme).
        
    Examples:
        >>> get_base_url("https://example.com/path?query=1#fragment")
        'https://example.com'
        >>> get_base_url("https://example.com/path?query=1#fragment", include_path=True)
        'https://example.com/path'
        >>> get_base_url("https://user:pass@example.com:8080/path")
        'https://user:pass@example.com:8080'
    """
    parsed = urlparse(url)
    if not parsed.scheme:
        raise ValueError("Invalid URL: missing scheme (e.g., 'http://' or 'https://')")
        
    base = f"{parsed.scheme}://{parsed.netloc}"
    
    if include_path and parsed.path:
        path = parsed.path.rstrip("/") if parsed.path != "/" else "/"
        base = f"{base}{path}"
    
    return base 