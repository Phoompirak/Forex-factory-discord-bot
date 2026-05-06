# Test Guide for Forex Factory Discord Bot

## Overview
This document describes how to run the test suite for the Forex Factory Discord Bot project.

## Test Structure
The tests are organized into the following files:

- **test_scraper.py** - Tests for the `scrape_forex_factory()` function
  - Tests successful scraping
  - Tests network error handling
  - Tests missing table handling
  - Tests N/A value handling
  - Tests missing cells handling

- **test_gemini_processor.py** - Tests for the Gemini AI processor
  - Tests `get_impact_emoji()` function
  - Tests `process_news_with_gemini()` function
  - Tests error handling and API failures
  - Tests various impact levels (High, Medium, Low, N/A)

- **test_discord_sender.py** - Tests for Discord message sending
  - Tests successful message sending
  - Tests missing webhook URL handling
  - Tests HTTP error handling
  - Tests various message formats with emojis
  - Tests long message handling

- **test_main.py** - Tests for the main bot orchestration
  - Tests successful bot run with multiple news items
  - Tests behavior when no news items are found
  - Tests rate limiting sleep behavior
  - Tests message formatting
  - Tests error handling throughout the pipeline

## Running Tests

### Prerequisites
Install test dependencies:
```bash
pip install -r requirements-test.txt
```

Or install main requirements:
```bash
pip install -r requirements.txt
```

### Run All Tests

#### Using unittest (built-in Python)
```bash
cd tests
python run_all_tests.py
```

Or from project root:
```bash
python -m unittest discover tests -p "test_*.py" -v
```

#### Using pytest (recommended)
```bash
pytest tests/ -v
```

Or for coverage report:
```bash
pytest tests/ --cov=. --cov-report=html
```

### Run Specific Test File
```bash
# Using unittest
python -m unittest tests.test_scraper -v

# Using pytest
pytest tests/test_scraper.py -v
```

### Run Specific Test Case
```bash
# Using unittest
python -m unittest tests.test_scraper.TestScrapeForexFactory.test_scrape_forex_factory_success -v

# Using pytest
pytest tests/test_scraper.py::TestScrapeForexFactory::test_scrape_forex_factory_success -v
```

## Test Coverage

Current test coverage includes:

### Scraper Module (7 tests)
- ✅ Successful scraping with valid HTML
- ✅ Network error handling
- ✅ Missing table handling
- ✅ Missing cells handling
- ✅ N/A values handling

### Gemini Processor Module (7 tests)
- ✅ Emoji mapping for all impact levels
- ✅ Successful processing with Gemini API
- ✅ Processing without impact marker
- ✅ API error handling with fallback
- ✅ N/A impact handling
- ✅ Missing field handling

### Discord Sender Module (7 tests)
- ✅ Successful message sending
- ✅ Missing webhook URL handling
- ✅ Empty webhook URL handling
- ✅ HTTP error handling
- ✅ Messages with various emojis
- ✅ Long message handling
- ✅ Payload structure validation

### Main Module (7 tests)
- ✅ Successful bot run with multiple news
- ✅ No news items handling
- ✅ Processing failure handling
- ✅ Rate limit sleep behavior
- ✅ Message format validation
- ✅ Scraping error handling
- ✅ Missing fields handling

**Total: 28+ unit tests**

## Mocking Strategy

All external API calls are mocked using `unittest.mock`:
- `requests.get()` for web scraping
- `requests.post()` for Discord webhook
- `google.generativeai` for Gemini API

This ensures:
- ✅ Tests run without external dependencies
- ✅ Tests are fast and deterministic
- ✅ No actual API calls during testing
- ✅ Can test error scenarios safely

## Continuous Integration

To set up CI/CD, you can add this to your CI configuration:

### GitHub Actions Example
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: 3.10
      - run: pip install -r requirements-test.txt
      - run: pytest tests/ -v --cov
```

## Notes

- All tests are isolated and can run in any order
- Tests use mocking to avoid external dependencies
- Each test is independent and doesn't require the others
- No API keys or credentials are needed to run tests
- All tests follow the AAA pattern: Arrange, Act, Assert

## Troubleshooting

If tests fail:

1. **Check Python version**: Ensure Python 3.8+ is installed
   ```bash
   python --version
   ```

2. **Check dependencies**:
   ```bash
   pip install -r requirements-test.txt
   ```

3. **Check path issues**:
   ```bash
   python -c "import sys; print(sys.path)"
   ```

4. **Run with verbose output**:
   ```bash
   pytest tests/ -vv -s
   ```

## Next Steps

1. ✅ Run the test suite
2. ✅ Verify all tests pass
3. ✅ Check code coverage
4. ✅ Set up CI/CD pipeline
5. ✅ Push to GitHub with confidence

## Questions?

Refer to the test files for detailed comments and examples in each test case.
