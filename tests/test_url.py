"""Tests for URL manipulation functions."""

import pytest

from vmstuff.url import get_base_url


@pytest.mark.parametrize(
    "url,include_path,expected",
    [
        # Basic URLs
        ("https://example.com", False, "https://example.com"),
        ("http://example.com", False, "http://example.com"),
        
        # URLs with paths
        (
            "https://example.com/path/to/something",
            False,
            "https://example.com"
        ),
        (
            "https://example.com/path/to/something",
            True,
            "https://example.com/path/to/something"
        ),
        
        # URLs with query parameters and fragments
        (
            "https://example.com/path?query=1#fragment",
            False,
            "https://example.com"
        ),
        (
            "https://example.com/path?query=1#fragment",
            True,
            "https://example.com/path"
        ),
        
        # URLs with authentication and ports
        (
            "https://user:pass@example.com:8080/path",
            False,
            "https://user:pass@example.com:8080"
        ),
        (
            "https://user:pass@example.com:8080/path",
            True,
            "https://user:pass@example.com:8080/path"
        ),
        
        # URLs with trailing slashes
        (
            "https://example.com/",
            True,
            "https://example.com/"
        ),
        (
            "https://example.com/path/",
            True,
            "https://example.com/path"
        ),
    ],
)
def test_get_base_url(url: str, include_path: bool, expected: str) -> None:
    """Test get_base_url function with various URL formats."""
    assert get_base_url(url, include_path=include_path) == expected


def test_get_base_url_invalid_url() -> None:
    """Test get_base_url with invalid URLs."""
    # Missing scheme
    with pytest.raises(ValueError):
        get_base_url("example.com") 