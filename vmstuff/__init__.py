"""
vmstuff - A collection of commonly used functions
"""

__version__ = "0.1.0"

from .network import HttpClient, RateLimitConfig, RetryConfig, rate_limit, with_retry
from .url import get_base_url

__all__ = [
    "get_base_url",
    "HttpClient",
    "RateLimitConfig",
    "RetryConfig",
    "rate_limit",
    "with_retry",
]
