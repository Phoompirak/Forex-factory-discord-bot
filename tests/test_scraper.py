import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import requests

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scraper import scrape_forex_factory


class TestScrapeForexFactory(unittest.TestCase):
    """Test cases for the scrape_forex_factory function"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_url = "https://www.forexfactory.com/calendar"
        
        # Sample HTML response
        self.sample_html = """
        <table class="calendar__table">
            <tbody>
                <tr class="calendar_row">
                    <td class="calendar__cell--time">08:30am</td>
                    <td class="calendar__cell--currency">USD</td>
                    <td class="calendar__cell--impact">
                        <img title="High Impact" src=""/>
                    </td>
                    <td class="calendar__cell--event">Non-Farm Employment Change</td>
                    <td class="calendar__cell--actual">272K</td>
                    <td class="calendar__cell--forecast">180K</td>
                    <td class="calendar__cell--previous">165K</td>
                </tr>
                <tr class="calendar_row">
                    <td class="calendar__cell--time">10:00am</td>
                    <td class="calendar__cell--currency">EUR</td>
                    <td class="calendar__cell--impact">
                        <img title="Low Impact" src=""/>
                    </td>
                    <td class="calendar__cell--event">Industrial Production</td>
                    <td class="calendar__cell--actual">0.2%</td>
                    <td class="calendar__cell--forecast">0.1%</td>
                    <td class="calendar__cell--previous">0.0%</td>
                </tr>
            </tbody>
        </table>
        """

    @patch('scraper.requests.get')
    def test_scrape_forex_factory_success(self, mock_get):
        """Test successful scraping of forex factory"""
        # Mock the response
        mock_response = MagicMock()
        mock_response.text = self.sample_html
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        # Call the function
        result = scrape_forex_factory(self.test_url)

        # Assertions
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 2)
        
        # Check first news item
        self.assertEqual(result[0]['time'], '08:30am')
        self.assertEqual(result[0]['currency'], 'USD')
        self.assertEqual(result[0]['event'], 'Non-Farm Employment Change')
        self.assertEqual(result[0]['actual'], '272K')
        
        # Check second news item
        self.assertEqual(result[1]['currency'], 'EUR')
        self.assertEqual(result[1]['impact'], 'Low')

    @patch('scraper.requests.get')
    def test_scrape_forex_factory_network_error(self, mock_get):
        """Test handling of network errors"""
        # Mock a network error
        mock_get.side_effect = requests.exceptions.RequestException("Network Error")

        # Call the function
        result = scrape_forex_factory(self.test_url)

        # Should return empty list on error
        self.assertEqual(result, [])

    @patch('scraper.requests.get')
    def test_scrape_forex_factory_no_table(self, mock_get):
        """Test handling when calendar table is not found"""
        # Mock response with no calendar table
        mock_response = MagicMock()
        mock_response.text = "<html><body>No table here</body></html>"
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        # Call the function
        result = scrape_forex_factory(self.test_url)

        # Should return empty list when table not found
        self.assertEqual(result, [])

    @patch('scraper.requests.get')
    def test_scrape_forex_factory_missing_cells(self, mock_get):
        """Test handling of rows with missing cells"""
        html_with_missing_cells = """
        <table class="calendar__table">
            <tbody>
                <tr class="calendar_row">
                    <td class="calendar__cell--currency">USD</td>
                </tr>
            </tbody>
        </table>
        """
        
        mock_response = MagicMock()
        mock_response.text = html_with_missing_cells
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        # Call the function
        result = scrape_forex_factory(self.test_url)

        # Should skip rows without time cell
        self.assertEqual(result, [])

    @patch('scraper.requests.get')
    def test_scrape_forex_factory_na_values(self, mock_get):
        """Test handling of N/A values in cells"""
        html_with_na = """
        <table class="calendar__table">
            <tbody>
                <tr class="calendar_row">
                    <td class="calendar__cell--time">08:30am</td>
                    <td class="calendar__cell--currency">USD</td>
                    <td class="calendar__cell--impact"></td>
                    <td class="calendar__cell--event">Test Event</td>
                    <td class="calendar__cell--actual">N/A</td>
                    <td class="calendar__cell--forecast">N/A</td>
                    <td class="calendar__cell--previous">N/A</td>
                </tr>
            </tbody>
        </table>
        """
        
        mock_response = MagicMock()
        mock_response.text = html_with_na
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        # Call the function
        result = scrape_forex_factory(self.test_url)

        # Should handle N/A values
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['actual'], 'N/A')


if __name__ == '__main__':
    unittest.main()
