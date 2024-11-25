import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup as bs
import json

from get_yahoo_comments import get_start_of_day
from get_yahoo_comments import get_end_of_day  
from get_yahoo_comments import get_stock_info
from get_yahoo_comments import score_comments
from get_yahoo_comments import get_conversation_info

def test_get_start_of_day_no_date():
    # Get the current date and calculate expected start-of-day timestamp
    now = datetime.now()
    expected_start_of_day = datetime(now.year, now.month, now.day, 0, 0, 0)
    expected_timestamp = int(expected_start_of_day.timestamp())

    # Call the function with no arguments
    result = get_start_of_day()

    # Assert the result matches the expected timestamp
    assert result == expected_timestamp, f"Expected {expected_timestamp}, got {result}"

def test_get_start_of_day_valid_date():
    # Test with a specific date
    test_date = "2024-11-22"
    expected_start_of_day = datetime(2024, 11, 22, 0, 0, 0)
    expected_timestamp = int(expected_start_of_day.timestamp())

    # Call the function with the test date
    result = get_start_of_day(test_date)

    # Assert the result matches the expected timestamp
    assert result == expected_timestamp, f"Expected {expected_timestamp}, got {result}"

def test_get_start_of_day_invalid_date():
    # Test with an invalid date string
    invalid_date = "22-11-2024"  # Incorrect format

    # Assert the function raises a ValueError
    with pytest.raises(ValueError, match="Invalid date format"):
        get_start_of_day(invalid_date)

def test_get_start_of_day_edge_case_leap_year():
    # Test with a leap year date
    leap_date = "2024-02-29"
    expected_start_of_day = datetime(2024, 2, 29, 0, 0, 0)
    expected_timestamp = int(expected_start_of_day.timestamp())

    # Call the function with the leap year date
    result = get_start_of_day(leap_date)

    # Assert the result matches the expected timestamp
    assert result == expected_timestamp, f"Expected {expected_timestamp}, got {result}"

def test_get_start_of_day_edge_case_end_of_year():
    # Test with the last day of the year
    end_of_year_date = "2023-12-31"
    expected_start_of_day = datetime(2023, 12, 31, 0, 0, 0)
    expected_timestamp = int(expected_start_of_day.timestamp())

    # Call the function with the end-of-year date
    result = get_start_of_day(end_of_year_date)

    # Assert the result matches the expected timestamp
    assert result == expected_timestamp, f"Expected {expected_timestamp}, got {result}"

def test_get_end_of_day_no_date():
    # Get the current date and calculate expected start-of-day timestamp
    now = datetime.now()
    expected_end_of_day = datetime(now.year, now.month, now.day, 0, 0, 0)
    expected_timestamp = int(expected_end_of_day.timestamp())

    # Call the function with no arguments
    result = get_end_of_day()

    # Assert the result matches the expected timestamp
    assert result == expected_timestamp, f"Expected {expected_timestamp}, got {result}"

def test_get_end_of_day_no_date():
    # Get the current date and calculate expected start-of-day timestamp
    now = datetime.now()
    expected_end_of_day = datetime(now.year, now.month, now.day, 23, 59, 59)
    expected_timestamp = int(expected_end_of_day.timestamp())

    # Call the function with no arguments
    result = get_end_of_day()

    # Assert the result matches the expected timestamp
    assert result == expected_timestamp, f"Expected {expected_timestamp}, got {result}"

def test_get_end_of_day_valid_date():
    # Test with a specific date
    test_date = "2024-11-22"
    expected_end_of_day = datetime(2024, 11, 22, 23, 59, 59)
    expected_timestamp = int(expected_end_of_day.timestamp())

    # Call the function with the test date
    result = get_end_of_day(test_date)

    # Assert the result matches the expected timestamp
    assert result == expected_timestamp, f"Expected {expected_timestamp}, got {result}"

def test_get_end_of_day_invalid_date():
    # Test with an invalid date string
    invalid_date = "22-11-2024"  # Incorrect format

    # Assert the function raises a ValueError
    with pytest.raises(ValueError, match="Invalid date format"):
        get_end_of_day(invalid_date)

def test_get_end_of_day_edge_case_leap_year():
    # Test with a leap year date
    leap_date = "2024-02-29"
    expected_end_of_day = datetime(2024, 2, 29, 23, 59, 59)
    expected_timestamp = int(expected_end_of_day.timestamp())

    # Call the function with the leap year date
    result = get_end_of_day(leap_date)

    # Assert the result matches the expected timestamp
    assert result == expected_timestamp, f"Expected {expected_timestamp}, got {result}"

def test_get_end_of_day_edge_case_end_of_year():
    # Test with the last day of the year
    end_of_year_date = "2023-12-31"
    expected_end_of_day = datetime(2023, 12, 31, 23, 59, 59)
    expected_timestamp = int(expected_end_of_day.timestamp())

    # Call the function with the end-of-year date
    result = get_end_of_day(end_of_year_date)

    # Assert the result matches the expected timestamp
    assert result == expected_timestamp, f"Expected {expected_timestamp}, got {result}"

def test_get_stock_info_valid_symbol():
    """Test with a valid stock symbol."""
    # Mock data to simulate yfinance response
    mock_info = {
        'currentPrice': 150.25,
        'dayLow': 148.0,
        'dayHigh': 152.0,
        'volume': 1200000,
        'previousClose': 149.5,
        'sharesShort': 20000,
    }

    # Patch the yfinance Ticker object
    with patch('get_yahoo_comments.yf.Ticker') as MockTicker:
        MockTicker.return_value.info = mock_info

        # Call the function with a valid symbol
        result = get_stock_info('AAPL')

        # Expected result
        expected_result = {
            'current_price': 150.25,
            'day_low': 148.0,
            'day_high': 152.0,
            'volume': 1200000,
            'previous_close': 149.5,
            'shares_short': 20000,
        }

        # Assert the result matches the expected output
        assert result == expected_result, f"Expected {expected_result}, got {result}"


def test_get_stock_info_missing_data():
    """Test when some fields are missing in the API response."""
    # Mock data with some fields missing
    mock_info = {
        'currentPrice': 150.25,
        'dayLow': 148.0,
        # 'dayHigh' is missing
        'volume': 1200000,
        # 'previousClose' is missing
        'sharesShort': 20000,
    }

    # Patch the yfinance Ticker object
    with patch('get_yahoo_comments.yf.Ticker') as MockTicker:
        MockTicker.return_value.info = mock_info

        # Call the function with a valid symbol
        result = get_stock_info('AAPL')

        # Expected result with None for missing fields
        expected_result = {
            'current_price': 150.25,
            'day_low': 148.0,
            'day_high': None,  # Missing field
            'volume': 1200000,
            'previous_close': None,  # Missing field
            'shares_short': 20000,
        }

        # Assert the result matches the expected output
        assert result == expected_result, f"Expected {expected_result}, got {result}"

def test_get_stock_info_invalid_symbol():
    """Test with an invalid stock symbol."""
    # Mock data for an invalid stock symbol
    mock_info = {}

    # Patch the yfinance Ticker object
    with patch('get_yahoo_comments.yf.Ticker') as MockTicker:
        MockTicker.return_value.info = mock_info

        # Call the function with an invalid symbol
        result = get_stock_info('INVALID')

        # Expected result with None for all fields
        expected_result = {
            'current_price': None,
            'day_low': None,
            'day_high': None,
            'volume': None,
            'previous_close': None,
            'shares_short': None,
        }

        # Assert the result matches the expected output
        assert result == expected_result, f"Expected {expected_result}, got {result}"

import pytest
from datetime import datetime
from get_yahoo_comments import score_comments

def test_score_comments_all_bullish():
    """Test with all bullish comments."""
    comments_data = [
        {"additional_data": {"labels": {"ids": ["BULLISH"]}}, "time": 1700774400},  # Timestamp: 2023-11-23 00:00:00
        {"additional_data": {"labels": {"ids": ["BULLISH"]}}, "time": 1700860800},  # Timestamp: 2023-11-24 00:00:00
    ]

    result = score_comments(comments_data)
    expected = {
        "bears": 0,
        "bear_users": [],
        "bulls": 2,
        "bull_users": [],
        "neutral": 0,
        "score": 2,
        "oldest_comment_ts": "2023-11-23 16:20:00",
        "newest_comment_ts": "2023-11-24 16:20:00",
    }
    assert result == expected, f"Expected {expected}, got {result}"


def test_score_comments_all_bearish():
    """Test with all bearish comments."""
    comments_data = [
        {"additional_data": {"labels": {"ids": ["BEARISH"]}}, "time": 1700774400},
        {"additional_data": {"labels": {"ids": ["BEARISH"]}}, "time": 1700860800},
    ]

    result = score_comments(comments_data)
    expected = {
        "bears": 2,
        "bear_users": [],
        "bulls": 0,
        "bull_users": [],
        "neutral": 0,
        "score": -2,
        "oldest_comment_ts": "2023-11-23 16:20:00",
        "newest_comment_ts": "2023-11-24 16:20:00",
    }
    assert result == expected, f"Expected {expected}, got {result}"


def test_score_comments_mixed_labels():
    """Test with mixed bullish, bearish, and neutral comments."""
    comments_data = [
        {"additional_data": {"labels": {"ids": ["BEARISH"]}}, "time": 1700774400},
        {"additional_data": {"labels": {"ids": ["BULLISH"]}}, "time": 1700860800},
        {"additional_data": {"labels": {"ids": []}}, "time": 1700947200},
    ]

    result = score_comments(comments_data)
    expected = {
        "bears": 1,
        "bear_users": [],
        "bulls": 1,
        "bull_users": [],
        "neutral": 1,
        "score": 0,
        "oldest_comment_ts": "2023-11-23 16:20:00",
        "newest_comment_ts": "2023-11-25 16:20:00",
    }
    assert result == expected, f"Expected {expected}, got {result}"


def test_score_comments_missing_labels():
    """Test with some comments missing labels."""
    comments_data = [
        {"additional_data": {"labels": {}}, "time": 1700774400},
        {"additional_data": {"labels": {"ids": ["BULLISH"]}}, "time": 1700860800},
        {"time": 1700947200},
    ]

    result = score_comments(comments_data)
    expected = {
        "bears": 0,
        "bear_users": [],
        "bulls": 1,
        "bull_users": [],
        "neutral": 2,
        "score": 1,
        "oldest_comment_ts": "2023-11-23 16:20:00",
        "newest_comment_ts": "2023-11-25 16:20:00",
    }
    assert result == expected, f"Expected {expected}, got {result}"


def test_score_comments_empty_input():
    """Test with an empty list of comments."""
    comments_data = []

    result = score_comments(comments_data)
    expected = {
        "bears": 0,
        "bear_users": [],
        "bulls": 0,
        "bull_users": [],
        "neutral": 0,
        "score": 0,
        "oldest_comment_ts": None,
        "newest_comment_ts": None,
    }
    assert result == expected, f"Expected {expected}, got {result}"

#TODO: Need to add definsive coding in case the remote API sends invalid timestamps 
#      before uncommenting this test
# def test_score_comments_invalid_timestamps():
#     """Test with invalid timestamps."""
#     comments_data = [
#         {"additional_data": {"labels": {"ids": ["BEARISH"]}}, "time": None},
#         {"additional_data": {"labels": {"ids": ["BULLISH"]}}, "time": "invalid"},
#     ]

#     result = score_comments(comments_data)
#     expected = {
#         "bears": 1,
#         "bear_users": [],
#         "bulls": 1,
#         "bull_users": [],
#         "neutral": 0,
#         "score": 0,
#         "oldest_comment_ts": None,
#         "newest_comment_ts": None,
#     }
#     assert result == expected, f"Expected {expected}, got {result}"

def test_get_conversation_info_valid_symbol():
    """Test with a valid symbol and valid HTML response."""
    # Mock the HTML response
    mock_html = """
    <html>
        <body>
            <script id="spotim-config">
                {"config": {"key": "value", "another_key": "another_value"}}
            </script>
        </body>
    </html>
    """
    # Mock the requests.get call
    with patch('get_yahoo_comments.requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.text = mock_html
        mock_get.return_value = mock_response

        # Call the function
        result = get_conversation_info('AAPL')

        # Expected data
        expected_result = {"key": "value", "another_key": "another_value"}

        # Assert the result matches the expected output
        assert result == expected_result, f"Expected {expected_result}, got {result}"

#TODO: if you put in an invalid symbol, a friendly error should be raised - 
#      instead there is a valueError NoneType
# def test_get_conversation_info_invalid_symbol():
#     """Test with an invalid symbol leading to missing spotim-config."""
#     # Mock the HTML response without `#spotim-config`
#     mock_html = """
#     <html>
#         <body>
#             <div>No relevant script here</div>
#         </body>
#     </html>
#     """
#     # Mock the requests.get call
#     with patch('get_yahoo_comments.requests.get') as mock_get:
#         mock_response = MagicMock()
#         mock_response.text = mock_html
#         mock_get.return_value = mock_response

#         # Call the function and expect an AttributeError
#         with pytest.raises(AttributeError, match="NoneType object has no attribute 'get_text'"):
#             get_conversation_info('INVALID')


def test_get_conversation_info_malformed_json():
    """Test with malformed JSON in the `spotim-config`."""
    # Mock the HTML response with invalid JSON
    mock_html = """
    <html>
        <body>
            <script id="spotim-config">
                {invalid_json: true, missing_quotes: true}
            </script>
        </body>
    </html>
    """
    # Mock the requests.get call
    with patch('get_yahoo_comments.requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.text = mock_html
        mock_get.return_value = mock_response

        # Call the function and expect a JSONDecodeError
        with pytest.raises(json.JSONDecodeError):
            get_conversation_info('AAPL')


def test_get_conversation_info_http_error():
    """Test when the HTTP request fails."""
    # Mock the requests.get call to raise an HTTP error
    with patch('get_yahoo_comments.requests.get') as mock_get:
        mock_get.side_effect = requests.exceptions.RequestException("HTTP error occurred")

        # Call the function and expect a RequestException
        with pytest.raises(requests.exceptions.RequestException, match="HTTP error occurred"):
            get_conversation_info('AAPL')

#TODO: Right now the script does not handle empty HTML - this needs added
# def test_get_conversation_info_empty_html():
#     """Test with an empty HTML response."""
#     # Mock an empty HTML response
#     mock_html = ""
#     # Mock the requests.get call
#     with patch('get_yahoo_comments.requests.get') as mock_get:
#         mock_response = MagicMock()
#         mock_response.text = mock_html
#         mock_get.return_value = mock_response

#         # Call the function and expect an AttributeError
#         with pytest.raises(AttributeError, match="NoneType object has no attribute 'get_text'"):
#             get_conversation_info('AAPL')
