"""HTML parsing utilities."""

from typing import Sequence
from selectolax.parser import HTMLParser


def get_all_links_from_html(html: str, *, base_url: str | None = None) -> list[str]:
    """Extract all links from <a> tags in HTML content.
    
    Args:
        html: The HTML content to parse.
        base_url: Optional base URL to resolve relative URLs.
            If provided, relative URLs will be joined with this base.
    
    Returns:
        A list of unique URLs found in href attributes.
        If base_url is provided, relative URLs will be resolved against it.
        
    Examples:
        >>> html = '''
        ... <div>
        ...   <a href="https://example.com">Link 1</a>
        ...   <a href="/path">Link 2</a>
        ...   <a>No href</a>
        ... </div>
        ... '''
        >>> get_all_links_from_html(html)
        ['https://example.com', '/path']
        
        >>> get_all_links_from_html(html, base_url="https://base.com")
        ['https://example.com', 'https://base.com/path']
    """
    parser = HTMLParser(html)
    links = []
    
    for a_tag in parser.css("a"):
        href = a_tag.attributes.get("href") if a_tag.attributes else None
        if not href or not href.strip():
            continue
            
        href = href.strip()
        if base_url and not (href.startswith("http://") or href.startswith("https://")):
            # Handle relative URLs
            if href.startswith("/"):
                href = f"{base_url.rstrip('/')}{href}"
            else:
                href = f"{base_url.rstrip('/')}/{href}"
                
        links.append(href)
    
    # Remove duplicates while preserving order
    return list(dict.fromkeys(links)) 