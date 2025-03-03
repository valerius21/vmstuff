"""Tests for network-related utilities."""

import asyncio
from datetime import timedelta
from unittest.mock import AsyncMock, patch

import httpx
import pytest
from pydantic import AnyHttpUrl

from vmstuff.network import HttpClient, RateLimitConfig, RetryConfig, rate_limit, with_retry


@pytest.mark.asyncio
async def test_http_client_basic():
    """Test basic HTTP client functionality."""
    async with HttpClient() as client:
        assert client.timeout == 30.0
        assert isinstance(client.rate_limit_config, RateLimitConfig)
        assert isinstance(client.retry_config, RetryConfig)


@pytest.mark.asyncio
async def test_http_client_custom_config():
    """Test HTTP client with custom configuration."""
    rate_config = RateLimitConfig(calls=5, period=2.0)
    retry_config = RetryConfig(max_tries=3, max_time=10)
    
    async with HttpClient(
        timeout=timedelta(seconds=15),
        rate_limit_config=rate_config,
        retry_config=retry_config,
        base_url="https://api.example.com",
    ) as client:
        assert client.timeout == 15.0
        assert client.rate_limit_config == rate_config
        assert client.retry_config == retry_config
        assert client.base_url == "https://api.example.com"


@pytest.mark.asyncio
async def test_http_client_get():
    """Test HTTP GET request."""
    mock_response = httpx.Response(200, json={"key": "value"})
    
    with patch("httpx.AsyncClient.get", AsyncMock(return_value=mock_response)):
        async with HttpClient() as client:
            response = await client.get(
                "https://api.example.com/data",
                params={"q": "test"},
                headers={"Authorization": "Bearer token"},
            )
            
            assert response.status_code == 200
            assert response.json() == {"key": "value"}


@pytest.mark.asyncio
async def test_http_client_post():
    """Test HTTP POST request."""
    mock_response = httpx.Response(201, json={"id": 1})
    
    with patch("httpx.AsyncClient.post", AsyncMock(return_value=mock_response)):
        async with HttpClient() as client:
            response = await client.post(
                "https://api.example.com/data",
                json={"name": "test"},
                headers={"Content-Type": "application/json"},
            )
            
            assert response.status_code == 201
            assert response.json() == {"id": 1}


@pytest.mark.asyncio
async def test_retry_decorator():
    """Test retry decorator functionality."""
    mock_func = AsyncMock(side_effect=[ValueError, ValueError, "success"])
    
    @with_retry(
        config=RetryConfig(max_tries=3),
        on_exceptions=(ValueError,),
    )
    async def test_func():
        return await mock_func()
    
    result = await test_func()
    assert result == "success"
    assert mock_func.call_count == 3


@pytest.mark.asyncio
async def test_rate_limit_decorator():
    """Test rate limit decorator functionality."""
    call_times = []
    
    @rate_limit(config=RateLimitConfig(calls=2, period=1.0))
    async def test_func():
        call_times.append(asyncio.get_running_loop().time())
    
    # Make 3 calls - the third should be delayed
    await test_func()
    await test_func()
    await test_func()
    
    assert len(call_times) == 3
    # Verify the third call was delayed by checking time difference
    assert call_times[2] - call_times[0] >= 1.0


@pytest.mark.asyncio
async def test_http_client_retry_on_error():
    """Test HTTP client retry on transport error."""
    mock_get = AsyncMock(
        side_effect=[
            httpx.TransportError("Connection failed"),
            httpx.TransportError("Still failed"),
            httpx.Response(200, json={"success": True}),
        ]
    )
    
    with patch("httpx.AsyncClient.get", mock_get):
        async with HttpClient(
            retry_config=RetryConfig(max_tries=3, jitter="none")
        ) as client:
            response = await client.get("https://api.example.com/data")
            
            assert response.status_code == 200
            assert response.json() == {"success": True}
            assert mock_get.call_count == 3 