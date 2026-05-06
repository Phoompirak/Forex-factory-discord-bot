import unittest
from unittest.mock import patch, MagicMock, call
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import run_bot


class TestRunBot(unittest.TestCase):
    """Test cases for the run_bot function"""

    @patch('main.send_to_discord')
    @patch('main.process_news_with_gemini')
    @patch('main.scrape_forex_factory')
    def test_run_bot_success(self, mock_scrape, mock_process, mock_send):
        """Test successful bot run with multiple news items"""
        # Mock scraped news items
        mock_scrape.return_value = [
            {
                'time': '08:30am',
                'currency': 'USD',
                'impact': 'High',
                'event': 'Non-Farm Employment Change',
                'actual': '272K',
                'forecast': '180K',
                'previous': '165K'
            },
            {
                'time': '10:00am',
                'currency': 'EUR',
                'impact': 'Low',
                'event': 'Industrial Production',
                'actual': '0.2%',
                'forecast': '0.1%',
                'previous': '0.0%'
            }
        ]

        # Mock processed news
        mock_process.side_effect = [
            {
                'emoji': '🔴',
                'gemini_impact_level': 'High',
                'original_news': mock_scrape.return_value[0],
                'summary': 'Employment data exceeded expectations'
            },
            {
                'emoji': '🟡',
                'gemini_impact_level': 'Low',
                'original_news': mock_scrape.return_value[1],
                'summary': 'Industrial production showed modest growth'
            }
        ]

        # Call the function
        run_bot()

        # Assertions
        mock_scrape.assert_called_once()
        self.assertEqual(mock_process.call_count, 2)
        self.assertEqual(mock_send.call_count, 2)

    @patch('main.send_to_discord')
    @patch('main.process_news_with_gemini')
    @patch('main.scrape_forex_factory')
    def test_run_bot_no_news(self, mock_scrape, mock_process, mock_send):
        """Test bot run when no news items are scraped"""
        # Mock empty scrape result
        mock_scrape.return_value = []

        # Call the function
        run_bot()

        # Assertions
        mock_scrape.assert_called_once()
        mock_process.assert_not_called()
        mock_send.assert_not_called()

    @patch('main.send_to_discord')
    @patch('main.process_news_with_gemini')
    @patch('main.scrape_forex_factory')
    def test_run_bot_process_returns_none(self, mock_scrape, mock_process, mock_send):
        """Test bot run when Gemini processing returns None"""
        # Mock scraped news
        mock_scrape.return_value = [
            {
                'time': '08:30am',
                'currency': 'USD',
                'impact': 'High',
                'event': 'Non-Farm Employment Change',
                'actual': '272K',
                'forecast': '180K',
                'previous': '165K'
            }
        ]

        # Mock process returning None
        mock_process.return_value = None

        # Call the function
        run_bot()

        # Assertions
        mock_scrape.assert_called_once()
        mock_process.assert_called_once()
        mock_send.assert_not_called()  # Should not send if process returns None

    @patch('main.time.sleep')
    @patch('main.send_to_discord')
    @patch('main.process_news_with_gemini')
    @patch('main.scrape_forex_factory')
    def test_run_bot_rate_limit_sleep(self, mock_scrape, mock_process, mock_send, mock_sleep):
        """Test that bot sleeps between messages to avoid rate limiting"""
        # Mock scraped news items
        mock_scrape.return_value = [
            {
                'time': '08:30am',
                'currency': 'USD',
                'impact': 'High',
                'event': 'Test Event 1',
                'actual': 'N/A',
                'forecast': 'N/A',
                'previous': 'N/A'
            },
            {
                'time': '09:30am',
                'currency': 'EUR',
                'impact': 'Low',
                'event': 'Test Event 2',
                'actual': 'N/A',
                'forecast': 'N/A',
                'previous': 'N/A'
            }
        ]

        # Mock processed news
        mock_process.side_effect = [
            {
                'emoji': '🔴',
                'gemini_impact_level': 'High',
                'original_news': mock_scrape.return_value[0],
                'summary': 'Test 1'
            },
            {
                'emoji': '🟡',
                'gemini_impact_level': 'Low',
                'original_news': mock_scrape.return_value[1],
                'summary': 'Test 2'
            }
        ]

        # Call the function
        run_bot()

        # Should sleep once between messages
        self.assertEqual(mock_sleep.call_count, 2)
        mock_sleep.assert_called_with(1)

    @patch('main.send_to_discord')
    @patch('main.process_news_with_gemini')
    @patch('main.scrape_forex_factory')
    def test_run_bot_message_format(self, mock_scrape, mock_process, mock_send):
        """Test that messages are formatted correctly"""
        # Mock news
        test_news = {
            'time': '08:30am',
            'currency': 'USD',
            'impact': 'High',
            'event': 'Non-Farm Employment Change',
            'actual': '272K',
            'forecast': '180K',
            'previous': '165K'
        }
        mock_scrape.return_value = [test_news]

        # Mock processed data
        mock_process.return_value = {
            'emoji': '🔴',
            'gemini_impact_level': 'High',
            'original_news': test_news,
            'summary': 'Strong employment data'
        }

        # Call the function
        run_bot()

        # Verify message format
        mock_send.assert_called_once()
        sent_message = mock_send.call_args[0][0]
        
        # Message should contain key information
        self.assertIn('🔴', sent_message)
        self.assertIn('High', sent_message)
        self.assertIn('USD', sent_message)
        self.assertIn('Non-Farm Employment Change', sent_message)
        self.assertIn('Summary:', sent_message)
        self.assertIn('08:30am', sent_message)
        self.assertIn('272K', sent_message)

    @patch('main.send_to_discord')
    @patch('main.process_news_with_gemini')
    @patch('main.scrape_forex_factory')
    def test_run_bot_scrape_error(self, mock_scrape, mock_process, mock_send):
        """Test bot run when scraping fails"""
        # Mock scrape returning empty list (like error case)
        mock_scrape.return_value = []

        # Call the function
        run_bot()

        # Should not attempt to process or send
        mock_process.assert_not_called()
        mock_send.assert_not_called()

    @patch('main.send_to_discord')
    @patch('main.process_news_with_gemini')
    @patch('main.scrape_forex_factory')
    def test_run_bot_with_missing_fields(self, mock_scrape, mock_process, mock_send):
        """Test bot run with news items containing N/A values"""
        # Mock news with N/A values
        mock_scrape.return_value = [
            {
                'time': 'N/A',
                'currency': 'JPY',
                'impact': 'N/A',
                'event': 'Bank Holiday',
                'actual': 'N/A',
                'forecast': 'N/A',
                'previous': 'N/A'
            }
        ]

        # Mock processed data
        mock_process.return_value = {
            'emoji': '🟢',
            'gemini_impact_level': 'No Impact',
            'original_news': mock_scrape.return_value[0],
            'summary': 'Bank holiday'
        }

        # Should handle gracefully
        run_bot()

        mock_send.assert_called_once()


if __name__ == '__main__':
    unittest.main()
