# Tests for LokisApi Python Library

This directory contains tests for the LokisApi Python library.

## Running Tests

### Install test dependencies

```bash
pip install -e ".[test]"
```

### Run all tests

```bash
pytest
```

### Run tests with coverage

```bash
pytest --cov=lokisapi
```

### Run specific test files

```bash
pytest tests/test_client.py
pytest tests/test_utils.py
```

### Run tests with verbose output

```bash
pytest -v
```

## Test Structure

- `test_client.py` - Tests for the main LokisApiClient class
- `test_utils.py` - Tests for utility functions
- `__init__.py` - Test package initialization

## Test Coverage

The tests cover:

- Client initialization and configuration
- Image generation and editing
- Chat completions with various parameters
- Thinking mode for Gemini 2.5 models
- Reasoning effort for GPT-5 models
- Model listing and information
- Error handling (authentication, rate limits, API errors)
- Utility functions for image processing
- Utility functions for model information
- Input validation

## Mocking

Tests use `unittest.mock` to mock HTTP requests and avoid making actual API calls during testing. This ensures:

- Tests run quickly
- Tests don't depend on external services
- Tests are reliable and repeatable
- No API keys are required for testing

## Adding New Tests

When adding new features to the library:

1. Add corresponding tests in the appropriate test file
2. Test both success and error cases
3. Use mocking for external dependencies
4. Include docstrings explaining what each test does
5. Follow the existing naming conventions (`test_*`)

## Continuous Integration

These tests are designed to run in CI/CD pipelines and should pass without requiring external API access or credentials.
