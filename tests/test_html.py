"""Tests for HTML parsing utilities."""

from vmstuff.html import get_all_links_from_html


def test_get_all_links_basic():
    """Test basic link extraction."""
    html = """
    <div>
        <a href="https://example.com">Link 1</a>
        <a href="/path">Link 2</a>
        <a>No href</a>
        <p>Not a link</p>
    </div>
    """
    
    links = get_all_links_from_html(html)
    assert links == ["https://example.com", "/path"]


def test_get_all_links_with_base_url():
    """Test link extraction with base URL resolution."""
    html = """
    <div>
        <a href="https://example.com">Absolute</a>
        <a href="/path">Root relative</a>
        <a href="page">Relative</a>
    </div>
    """
    
    links = get_all_links_from_html(html, base_url="https://base.com")
    assert links == [
        "https://example.com",
        "https://base.com/path",
        "https://base.com/page",
    ]


def test_get_all_links_duplicates():
    """Test duplicate link handling."""
    html = """
    <div>
        <a href="https://example.com">Link 1</a>
        <a href="https://example.com">Link 1 again</a>
        <a href="/path">Link 2</a>
        <a href="/path">Link 2 again</a>
    </div>
    """
    
    links = get_all_links_from_html(html)
    assert links == ["https://example.com", "/path"]


def test_get_all_links_empty():
    """Test empty HTML and no links."""
    assert get_all_links_from_html("") == []
    assert get_all_links_from_html("<div>No links here</div>") == []


def test_get_all_links_malformed():
    """Test malformed HTML handling."""
    html = """
    <div>
        <a href="https://example.com">Valid</a>
        <a href="">Empty href</a>
        <a href="   ">Whitespace href</a>
        <a href="https://example2.com"/>
    </div>
    """
    
    links = get_all_links_from_html(html)
    assert links == ["https://example.com", "https://example2.com"]


def test_get_all_links_base_url_trailing_slash():
    """Test base URL handling with trailing slashes."""
    html = '<a href="page">Link</a>'
    
    # Base URL with trailing slash
    links1 = get_all_links_from_html(html, base_url="https://base.com/")
    assert links1 == ["https://base.com/page"]
    
    # Base URL without trailing slash
    links2 = get_all_links_from_html(html, base_url="https://base.com")
    assert links2 == ["https://base.com/page"] 