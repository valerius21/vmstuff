# vmstuff

A Python package containing commonly used functions.

## Requirements

- Python >=3.13.2
- uv (for package management)

## Installation

First, create and activate a virtual environment:
```bash
uv venv
source .venv/bin/activate  # On Unix/Linux
# or
.venv\Scripts\activate  # On Windows
```

Then install the package:
```bash
uv pip install -e .
```

## Features

- Common helper functions
- Modern Python features (3.13+)
- Type annotations throughout

## Usage

```python
from vmstuff import get_base_url

# Extract base URL without path
base = get_base_url("https://example.com/path?query=1#fragment")
print(base)  # Output: https://example.com

# Include the path component
base_with_path = get_base_url("https://example.com/path?query=1#fragment", include_path=True)
print(base_with_path)  # Output: https://example.com/path

# Invalid URLs will raise ValueError
try:
    get_base_url("example.com")  # Missing scheme
except ValueError as e:
    print(e)  # Output: Invalid URL: missing scheme (e.g., 'http://' or 'https://')
```

## Development

To set up the development environment:

1. Clone the repository
2. Create and activate a virtual environment:
   ```bash
   uv venv
   source .venv/bin/activate  # On Unix/Linux
   # or
   .venv\Scripts\activate  # On Windows
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
