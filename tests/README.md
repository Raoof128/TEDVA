# Test Suite

Automated tests for the Purple Team Validation Framework.

## Running Tests

### Install Test Dependencies

```bash
pip install -r requirements-dev.txt
```

### Run All Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=automation_scripts --cov-report=html

# Run specific test file
pytest tests/test_attack_matrix_builder.py

# Run with verbose output
pytest -v

# Run specific test
pytest tests/test_attack_matrix_builder.py::TestAtomicTestMatrix::test_initialization
```

## Test Structure

```
tests/
├── __init__.py                       # Test package initialization
├── conftest.py                       # Shared fixtures and configuration
├── test_attack_matrix_builder.py    # Tests for attack matrix builder
└── README.md                         # This file
```

## Test Coverage

Current test coverage targets:
- **Unit Tests:** Core functionality of each module
- **Integration Tests:** End-to-end workflow testing
- **Validation Tests:** Configuration and data validation

## Writing Tests

### Test Naming Convention

- Test files: `test_<module_name>.py`
- Test classes: `Test<ClassName>`
- Test methods: `test_<functionality>`

### Example Test

```python
import pytest

def test_example():
    """Test description"""
    # Arrange
    input_data = {"key": "value"}

    # Act
    result = process_data(input_data)

    # Assert
    assert result["key"] == "expected_value"
```

### Using Fixtures

```python
def test_with_fixture(sample_test_matrix):
    """Test using shared fixture"""
    assert "test_plan" in sample_test_matrix
    assert len(sample_test_matrix["test_plan"]) > 0
```

## Continuous Integration

Tests run automatically on:
- Push to main/develop branches
- Pull requests
- Manual workflow dispatch

See `.github/workflows/validation.yml` for CI configuration.

## Test Data

Test data and fixtures are located in:
- `tests/conftest.py` - Shared fixtures
- `tests/data/` - Sample data files (if applicable)

## Contributing Tests

When adding new features:
1. Write tests for new functionality
2. Ensure existing tests still pass
3. Aim for >80% code coverage
4. Document complex test scenarios

See [CONTRIBUTING.md](../CONTRIBUTING.md) for more details.
