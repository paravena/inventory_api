# Testing Guide

## Overview

The Inventory Management API includes a comprehensive test suite that covers:
- API endpoints testing
- Model functionality testing
- Integration testing
- Edge cases and error handling

## Test Setup

1. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Unix/macOS
   # or
   .venv\Scripts\activate     # On Windows
   ```

2. Install test dependencies:
   ```bash
   pip install -r requirements-test.txt
   ```

3. Ensure you're in the project root directory:
   ```bash
   # Your current directory should contain pytest.ini
   ls pytest.ini
   ```

4. Verify environment setup:
   ```bash
   # Should show the virtual environment Python
   which python
   # Should list all test dependencies
   pip list
   ```

## Running Tests

### Running All Tests
To run the complete test suite, use:
```bash
python -m pytest
```

Note: While both `pytest` and `python -m pytest` commands are commonly used to run tests, in this project you should use `python -m pytest`. This is because `python -m pytest` adds the current directory to the Python path, which is necessary for the test suite to properly import modules from the `app` package. Running `pytest` directly might fail because it doesn't modify the Python path in the same way.

### Running Specific Test Files
```bash
# Run specific test file
python -m pytest tests/test_api.py
python -m pytest tests/test_models.py
python -m pytest tests/test_inventory.py
python -m pytest tests/test_products.py
```

### Running Tests with Coverage
```bash
pytest --cov=app tests/
```

To generate HTML coverage reports:
```bash
pytest --cov=app --cov-report=html tests/
```
Coverage reports will be available in the `htmlcov` directory.

## Test Structure

### API Tests (`test_api.py`)
- Tests for inventory creation
- Error handling for invalid inputs
- Duplicate inventory checks

### Product Tests (`test_products.py`)
- CRUD operations for products
- Filtering and pagination
- Error cases (duplicate SKUs, invalid data)

### Inventory Tests (`test_inventory.py`)
- Inventory management operations
- Stock transfers between stores
- Low stock alerts
- Error handling for insufficient stock

### Model Tests (`test_models.py`)
- Data model validation
- Relationship testing
- Data conversion and serialization

## Test Configuration

The project uses pytest configuration in `pytest.ini`:
- Test files pattern: `test_*.py`
- Test function pattern: `test_*`
- Test directory: `tests/`

## Writing New Tests

### Test Fixtures
Common fixtures are available in `conftest.py`:
- `client`: Flask test client
- `database`: Test database session
- `sample_product`: Sample product data
- `sample_inventory`: Sample inventory data

### Example Test Structure
```python
def test_feature_success(client, database):
    # Arrange
    # Set up test data

    # Act
    response = client.post('/api/endpoint', json={
        'key': 'value'
    })

    # Assert
    assert response.status_code == 200
    assert response.json['result'] == 'expected'
```

## Continuous Integration

Tests are automatically run in the CI pipeline for:
- Pull requests
- Merges to main branch
- Release tags

## Troubleshooting

### Common Test Issues

1. **Module Import Issues**
   - Always run tests from the project root directory
   - Ensure you're using the correct virtual environment
   - Verify that PYTHONPATH includes the project root
   - Check that all necessary __init__.py files are present in:
     - app/
     - app/models/
     - app/routes/
     - tests/

2. **Database Errors**
   - Ensure test database is properly configured
   - Check if migrations are up to date
   - Verify database cleanup between tests

2. **Failed Assertions**
   - Check test data setup
   - Verify expected vs actual results
   - Review related business logic

3. **Coverage Issues**
   - Identify uncovered code paths
   - Add missing test cases
   - Review edge cases
