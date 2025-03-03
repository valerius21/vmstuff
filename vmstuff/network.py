"""Network-related utilities including retry, rate limiting, and HTTP operations."""

from __future__ import annotations

import asyncio
import functools
import random
import time
from collections.abc import Callable, Awaitable
from datetime import timedelta
from typing import Any, Literal, ParamSpec, TypeVar, cast, overload

import backoff
import httpx
from pydantic import AnyHttpUrl, BaseModel, ConfigDict
from ratelimit import RateLimitDecorator, sleep_and_retry

P = ParamSpec("P")
R = TypeVar("R")
T = TypeVar("T")

class RateLimitConfig(BaseModel):
    """Configuration for rate limiting."""
    model_config = ConfigDict(frozen=True)
    
    calls: int = 10
    period: float = 1.0

class RetryConfig(BaseModel):
    """Configuration for retry behavior."""
    model_config = ConfigDict(frozen=True)
    
    max_tries: int = 5
    max_time: float = 30
    jitter: Literal["full", "none"] = "full"
    
    def get_jitter_func(self) -> Callable[[float], float] | None:
        """Get the jitter function based on configuration."""
        if self.jitter == "full":
            return lambda value: random.uniform(0, value)
        return None

@overload
def with_retry(
    *,
    config: RetryConfig | None = None,
    on_exceptions: tuple[type[Exception], ...] = (Exception,),
) -> Callable[[Callable[P, Awaitable[T]]], Callable[P, Awaitable[T]]]: ...

@overload
def with_retry(
    *,
    config: RetryConfig | None = None,
    on_exceptions: tuple[type[Exception], ...] = (Exception,),
) -> Callable[[Callable[P, T]], Callable[P, T]]: ...

def with_retry(
    *,
    config: RetryConfig | None = None,
    on_exceptions: tuple[type[Exception], ...] = (Exception,),
) -> Callable[[Callable[P, Any]], Callable[P, Any]]:
    """Decorator for retrying operations with exponential backoff.
    
    Args:
        config: Retry configuration. If None, uses default settings.
        on_exceptions: Tuple of exceptions to retry on.
    
    Returns:
        A decorator that retries the function on specified exceptions.
    
    Examples:
        >>> @with_retry(on_exceptions=(ConnectionError,))
        ... async def fetch_data():
        ...     return await some_api_call()
    """
    retry_config = config or RetryConfig()
    
    def decorator(func: Callable[P, Any]) -> Callable[P, Any]:
        if asyncio.iscoroutinefunction(func):
            @functools.wraps(func)
            @backoff.on_exception(
                backoff.expo,
                on_exceptions,
                max_tries=retry_config.max_tries,
                max_time=retry_config.max_time,
                jitter=retry_config.get_jitter_func(),
            )
            async def async_wrapper(*args: P.args, **kwargs: P.kwargs) -> Any:
                return await func(*args, **kwargs)
            return async_wrapper
        else:
            @functools.wraps(func)
            @backoff.on_exception(
                backoff.expo,
                on_exceptions,
                max_tries=retry_config.max_tries,
                max_time=retry_config.max_time,
                jitter=retry_config.get_jitter_func(),
            )
            def sync_wrapper(*args: P.args, **kwargs: P.kwargs) -> Any:
                return func(*args, **kwargs)
            return sync_wrapper
    return decorator

def rate_limit(
    *, config: RateLimitConfig | None = None
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Decorator for rate limiting function calls.
    
    Args:
        config: Rate limit configuration. If None, uses default settings.
    
    Returns:
        A decorator that rate limits the function calls.
    
    Examples:
        >>> @rate_limit(config=RateLimitConfig(calls=100, period=60))
        ... async def api_call():
        ...     return await some_api_call()
    """
    rate_config = config or RateLimitConfig()
    
    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(func)
        @sleep_and_retry
        @RateLimitDecorator(
            calls=rate_config.calls,
            period=rate_config.period,
        )
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            return func(*args, **kwargs)
        return wrapper
    return decorator

class HttpClient:
    """HTTP client with sensible defaults and built-in retry/rate limiting."""
    
    def __init__(
        self,
        *,
        timeout: float | timedelta = 30.0,
        rate_limit_config: RateLimitConfig | None = None,
        retry_config: RetryConfig | None = None,
        base_url: str | None = None,
    ) -> None:
        """Initialize the HTTP client.
        
        Args:
            timeout: Request timeout in seconds or as timedelta.
            rate_limit_config: Rate limiting configuration.
            retry_config: Retry configuration.
            base_url: Optional base URL for all requests.
        """
        if isinstance(timeout, timedelta):
            timeout = timeout.total_seconds()
            
        self.timeout = timeout
        self.rate_limit_config = rate_limit_config or RateLimitConfig()
        self.retry_config = retry_config or RetryConfig()
        self.base_url = base_url
        
        self._client = httpx.AsyncClient(
            timeout=timeout,
            base_url=base_url or "",
            follow_redirects=True,
        )
        
    async def __aenter__(self) -> HttpClient:
        return self
        
    async def __aexit__(self, *_: Any) -> None:
        await self.close()
        
    async def close(self) -> None:
        """Close the underlying HTTP client."""
        await self._client.aclose()
        
    @rate_limit()
    @with_retry(on_exceptions=(httpx.TransportError, httpx.TimeoutException))
    async def get(
        self,
        url: str | AnyHttpUrl,
        *,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> httpx.Response:
        """Send a GET request.
        
        Args:
            url: The URL to request.
            params: Optional query parameters.
            headers: Optional request headers.
            
        Returns:
            The HTTP response.
            
        Examples:
            >>> async with HttpClient() as client:
            ...     response = await client.get("https://api.example.com/data")
            ...     data = response.json()
        """
        return await self._client.get(
            str(url),
            params=params,
            headers=headers,
        )
        
    @rate_limit()
    @with_retry(on_exceptions=(httpx.TransportError, httpx.TimeoutException))
    async def post(
        self,
        url: str | AnyHttpUrl,
        *,
        json: Any | None = None,
        data: Any | None = None,
        headers: dict[str, str] | None = None,
    ) -> httpx.Response:
        """Send a POST request.
        
        Args:
            url: The URL to request.
            json: Optional JSON data.
            data: Optional form data.
            headers: Optional request headers.
            
        Returns:
            The HTTP response.
            
        Examples:
            >>> async with HttpClient() as client:
            ...     response = await client.post(
            ...         "https://api.example.com/data",
            ...         json={"key": "value"}
            ...     )
        """
        return await self._client.post(
            str(url),
            json=json,
            data=data,
            headers=headers,
        ) 