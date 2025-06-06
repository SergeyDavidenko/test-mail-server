# 🧪 Test Mail Server Testing

## Quick Start with run_tests.sh

The easiest way to run tests - use the ready-made script:

```bash
# Quick basic tests (recommended for start)
./run_tests.sh quick

# All working tests
./run_tests.sh working

# Tests with code coverage analysis
./run_tests.sh coverage

# Help for all commands
./run_tests.sh help
```

## Installing Testing Dependencies

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Or pytest separately
pip install pytest pytest-asyncio httpx pytest-cov
```

## Basic Commands

### Run all tests
```bash
pytest
```

### Detailed output
```bash
pytest -v
```

### Specific test file
```bash
pytest tests/test_simple.py
pytest tests/test_config.py
pytest tests/test_email_storage.py
```

### Specific test
```bash
pytest tests/test_simple.py::test_config_basic
```

## Test Markers

### Only unit tests
```bash
pytest -m unit
```

### Only integration tests
```bash
pytest -m integration
```

### Exclude slow tests
```bash
pytest -m "not slow"
```

## Code Coverage

### Show coverage
```bash
pytest --cov=app
```

### HTML coverage report
```bash
pytest --cov=app --cov-report=html
open htmlcov/index.html  # macOS
```

## Useful Options

### Stop on first error
```bash
pytest -x
```

### Run only failed tests
```bash
pytest --lf
```

### Show local variables on error
```bash
pytest -l
```

### Brief output
```bash
pytest -q
```

## Test Structure

```
tests/
├── conftest.py          # pytest configuration and fixtures
├── test_config.py       # Test configuration
├── test_email_storage.py # Email storage tests
├── test_api.py          # API endpoint tests
└── test_simple.py       # Simple demo tests
```

## Fixtures

Use ready-made fixtures from `conftest.py`:

```python
def test_example(test_client, api_key, auth_headers, sample_email):
    """Example usage of fixtures"""
    response = test_client.get("/api/v1/addresses", headers=auth_headers)
    assert response.status_code == 200
```

## Creating New Tests

### Test for new service
```python
import pytest
from app.services.your_service import YourService

class TestYourService:
    @pytest.fixture
    def service(self):
        return YourService()
    
    def test_your_method(self, service):
        result = service.your_method()
        assert result is not None
```

### API test
```python
def test_new_endpoint(test_client, auth_headers):
    response = test_client.get("/api/v1/new-endpoint", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "expected_field" in data
```

## Docker Testing

### In Docker container
```bash
# Through Makefile
make test

# Directly
docker run --rm test-mail-server pytest
```

### Testing in CI/CD
```yaml
# Example for GitHub Actions
- name: Run tests
  run: |
    pip install -r requirements-dev.txt
    pytest --cov=app --cov-report=xml
```

## Test Debugging

### With debugger
```bash
pytest --pdb
```

### Detailed error information
```bash
pytest --tb=long
```

### Show print() in tests
```bash
pytest -s
```

## Example Commands

```bash
# Quick tests for development
pytest tests/test_simple.py -v

# Full testing before commit
pytest --cov=app --cov-report=term-missing

# Testing specific component
pytest tests/test_email_storage.py -v

# Only configuration tests
pytest tests/test_config.py::TestConfig::test_default_values
```

## Performance

### Parallel execution (if pytest-xdist installed)
```bash
pip install pytest-xdist
pytest -n auto
```

### Test profiling
```bash
pytest --durations=10
```

## Code Quality Monitoring

### Coverage check
```bash
pytest --cov=app --cov-fail-under=80
```

### Integration with pre-commit
```bash
pip install pre-commit
pre-commit install
```

---

**Quick start for testing:**

1. `pip install -r requirements-dev.txt`
2. `pytest tests/test_simple.py -v`
3. `pytest --cov=app`

🎯 **For CI/CD:** `pytest --cov=app --cov-report=xml` 