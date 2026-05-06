import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gemini_processor import process_news_with_gemini, get_impact_emoji


class TestGetImpactEmoji(unittest.TestCase):
    """Test cases for the get_impact_emoji function"""

    def test_high_impact_emoji(self):
        """Test emoji for high impact"""
        result = get_impact_emoji("High")
        self.assertEqual(result, "🔴")
        
        result = get_impact_emoji("High Impact")
        self.assertEqual(result, "🔴")

    def test_medium_impact_emoji(self):
        """Test emoji for medium impact"""
        result = get_impact_emoji("Medium")
        self.assertEqual(result, "🟠")
        
        result = get_impact_emoji("Medium Impact")
        self.assertEqual(result, "🟠")

    def test_low_impact_emoji(self):
        """Test emoji for low impact"""
        result = get_impact_emoji("Low")
        self.assertEqual(result, "🟡")
        
        result = get_impact_emoji("Low Impact")
        self.assertEqual(result, "🟡")

    def test_no_impact_emoji(self):
        """Test emoji for no impact or unknown"""
        result = get_impact_emoji("N/A")
        self.assertEqual(result, "🟢")
        
        result = get_impact_emoji("Unknown")
        self.assertEqual(result, "🟢")


class TestProcessNewsWithGemini(unittest.TestCase):
    """Test cases for the process_news_with_gemini function"""

    def setUp(self):
        """Set up test fixtures"""
        self.sample_news_high = {
            'time': '08:30am',
            'currency': 'USD',
            'impact': 'High',
            'event': 'Non-Farm Employment Change',
            'actual': '272K',
            'forecast': '180K',
            'previous': '165K'
        }

        self.sample_news_low = {
            'time': '10:00am',
            'currency': 'EUR',
            'impact': 'Low',
            'event': 'Industrial Production',
            'actual': '0.2%',
            'forecast': '0.1%',
            'previous': '0.0%'
        }

        self.sample_news_na = {
            'time': '11:00am',
            'currency': 'JPY',
            'impact': 'N/A',
            'event': 'Bank Holiday',
            'actual': 'N/A',
            'forecast': 'N/A',
            'previous': 'N/A'
        }

    @patch('gemini_processor.model')
    def test_process_news_success_with_impact(self, mock_model):
        """Test successful processing with clear impact in response"""
        # Mock Gemini response
        mock_response = MagicMock()
        mock_response.text = "Summary: The employment data exceeded expectations significantly. Impact: High"
        mock_model.generate_content.return_value = mock_response

        # Call the function
        result = process_news_with_gemini(self.sample_news_high)

        # Assertions
        self.assertIsNotNone(result)
        self.assertEqual(result['original_news'], self.sample_news_high)
        self.assertIn('summary', result)
        self.assertIn('gemini_impact_level', result)
        self.assertIn('emoji', result)
        self.assertEqual(result['emoji'], '🔴')

    @patch('gemini_processor.model')
    def test_process_news_success_without_impact(self, mock_model):
        """Test successful processing without impact marker in response"""
        # Mock Gemini response without "Impact:" marker
        mock_response = MagicMock()
        mock_response.text = "Summary: The employment data exceeded expectations significantly."
        mock_model.generate_content.return_value = mock_response

        # Call the function
        result = process_news_with_gemini(self.sample_news_high)

        # Assertions
        self.assertIsNotNone(result)
        self.assertEqual(result['original_news'], self.sample_news_high)
        # Should fallback to scraped impact
        self.assertEqual(result['gemini_impact_level'], 'High')

    @patch('gemini_processor.model')
    def test_process_news_api_error(self, mock_model):
        """Test error handling when Gemini API fails"""
        # Mock Gemini API error
        mock_model.generate_content.side_effect = Exception("API Error")

        # Call the function
        result = process_news_with_gemini(self.sample_news_high)

        # Should fallback gracefully
        self.assertIsNotNone(result)
        self.assertEqual(result['original_news'], self.sample_news_high)
        self.assertIn('Could not generate summary', result['summary'])
        self.assertEqual(result['gemini_impact_level'], 'High')
        self.assertEqual(result['emoji'], '🔴')

    @patch('gemini_processor.model')
    def test_process_news_na_impact(self, mock_model):
        """Test processing with N/A impact level"""
        # Mock Gemini response
        mock_response = MagicMock()
        mock_response.text = "Summary: Bank holiday - no trading activity. Impact: No Impact"
        mock_model.generate_content.return_value = mock_response

        # Call the function
        result = process_news_with_gemini(self.sample_news_na)

        # Assertions
        self.assertIsNotNone(result)
        self.assertEqual(result['emoji'], '🟢')

    @patch('gemini_processor.model')
    def test_process_news_missing_fields(self, mock_model):
        """Test processing with missing fields in news item"""
        # Incomplete news item
        incomplete_news = {
            'event': 'Test Event'
        }

        # Mock Gemini response
        mock_response = MagicMock()
        mock_response.text = "Summary: Test summary. Impact: Medium"
        mock_model.generate_content.return_value = mock_response

        # Call the function - should handle missing fields
        result = process_news_with_gemini(incomplete_news)

        # Should still work with N/A for missing fields
        self.assertIsNotNone(result)
        self.assertEqual(result['original_news']['event'], 'Test Event')

    @patch('gemini_processor.model')
    def test_process_news_with_various_impacts(self, mock_model):
        """Test processing with various impact levels"""
        test_cases = [
            (self.sample_news_low, '🟡'),
            (self.sample_news_na, '🟢'),
        ]

        for news, expected_emoji in test_cases:
            with self.subTest(news=news):
                # Mock response
                mock_response = MagicMock()
                mock_response.text = f"Summary: Test. Impact: {news['impact']}"
                mock_model.generate_content.return_value = mock_response

                result = process_news_with_gemini(news)
                self.assertEqual(result['emoji'], expected_emoji)


if __name__ == '__main__':
    unittest.main()
