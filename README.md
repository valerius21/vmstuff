# vmstuff

A Python package containing commonly used functions.

## Requirements

- Python >=3.13.2
- uv (for package management)

## Installation

First, create and activate a virtual environment:
```bash
uv venv
source .venv/bin/activate
```

Then install the package:
```bash
uv pip install -e .
```

## Features

- URL manipulation and validation
- HTTP client with retry and rate limiting
- Modern Python features (3.13+)
- Type annotations throughout

## Usage

### URL Manipulation

```python
from vmstuff import get_base_url

# Extract base URL without path
base = get_base_url("https://example.com/path?query=1#fragment")
print(base)  # https://example.com

# Include the path component
base_with_path = get_base_url("https://example.com/path?query=1#fragment", include_path=True)
print(base_with_path)  # https://example.com/path
```

### HTTP Client with Retry and Rate Limiting

```python
from vmstuff import HttpClient, RetryConfig, RateLimitConfig
from datetime import timedelta

# Basic usage
async with HttpClient() as client:
    response = await client.get("https://api.example.com/data")
    data = response.json()

# Custom configuration
retry_config = RetryConfig(
    max_tries=3,
    max_time=30,
    jitter="full"  # or "none"
)

rate_config = RateLimitConfig(
    calls=100,  # max calls
    period=60.0  # per 60 seconds
)

async with HttpClient(
    timeout=timedelta(seconds=30),
    retry_config=retry_config,
    rate_limit_config=rate_config,
    base_url="https://api.example.com"
) as client:
    # GET request with parameters
    response = await client.get(
        "/users",
        params={"page": 1},
        headers={"Authorization": "Bearer token"}
    )
    
    # POST request with JSON data
    response = await client.post(
        "/data",
        json={"key": "value"},
        headers={"Content-Type": "application/json"}
    )
```

### Retry Decorator

```python
from vmstuff import with_retry

@with_retry(
    config=RetryConfig(max_tries=3),
    on_exceptions=(ConnectionError, TimeoutError)
)
async def fetch_data():
    # This function will retry up to 3 times on connection or timeout errors
    return await some_api_call()
```

### Rate Limit Decorator

```python
from vmstuff import rate_limit

@rate_limit(config=RateLimitConfig(calls=100, period=60))
async def api_call():
    # This function is limited to 100 calls per 60 seconds
    return await some_api_call()
```

## Development

To set up the development environment:

1. Clone the repository
2. Create and activate a virtual environment:
   ```bash
   uv venv
   source .venv/bin/activate
   ```
3. Install development dependencies:
   ```bash
   uv pip install -e ".[dev]"
   ```

### Running Tests

Run all tests with coverage:
```bash
pytest
```

Run tests for a specific module:
```bash
pytest tests/test_url.py
```

Run tests with verbose output:
```bash
pytest -v
```

View coverage report in terminal:
```bash
pytest --cov=vmstuff --cov-report=term-missing
```

## License

MIT License
