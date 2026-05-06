import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from discord_sender import send_to_discord


class TestSendToDiscord(unittest.TestCase):
    """Test cases for the send_to_discord function"""

    @patch('discord_sender.DISCORD_WEBHOOK_URL', 'https://discord.com/api/webhooks/123/456')
    @patch('discord_sender.requests.post')
    def test_send_to_discord_success(self, mock_post):
        """Test successful message sending to Discord"""
        # Mock the response
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        # Test message
        test_message = "🔴 **High Impact News!** USD - Non-Farm Employment Change\n" \
                       "Summary: Test summary\n" \
                       "Time: 08:30am | Actual: 272K | Forecast: 180K | Previous: 165K"

        # Call the function
        send_to_discord(test_message)

        # Assertions
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        self.assertIn('https://discord.com/api/webhooks/123/456', str(call_args))
        
        # Check payload
        payload = call_args.kwargs['json']
        self.assertEqual(payload['content'], test_message)

    @patch('discord_sender.DISCORD_WEBHOOK_URL', None)
    def test_send_to_discord_no_webhook_url(self, ):
        """Test handling when webhook URL is not configured"""
        test_message = "Test message"
        
        # Should not raise an error, just return
        send_to_discord(test_message)

    @patch('discord_sender.DISCORD_WEBHOOK_URL', '')
    def test_send_to_discord_empty_webhook_url(self):
        """Test handling when webhook URL is empty string"""
        test_message = "Test message"
        
        # Should not raise an error, just return
        send_to_discord(test_message)

    @patch('discord_sender.DISCORD_WEBHOOK_URL', 'https://discord.com/api/webhooks/123/456')
    @patch('discord_sender.requests.post')
    def test_send_to_discord_http_error(self, mock_post):
        """Test handling of HTTP errors"""
        # Mock HTTP error
        mock_post.side_effect = Exception("HTTP Error 403")

        test_message = "Test message"
        
        # Should handle error gracefully and not raise
        send_to_discord(test_message)
        
        # Verify that post was called
        mock_post.assert_called_once()

    @patch('discord_sender.DISCORD_WEBHOOK_URL', 'https://discord.com/api/webhooks/123/456')
    @patch('discord_sender.requests.post')
    def test_send_to_discord_with_emojis(self, mock_post):
        """Test sending messages with various emojis"""
        # Mock the response
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        # Test message with emojis
        test_messages = [
            "🔴 High Impact",
            "🟠 Medium Impact",
            "🟡 Low Impact",
            "🟢 No Impact",
        ]

        for message in test_messages:
            with self.subTest(message=message):
                mock_post.reset_mock()
                send_to_discord(message)
                mock_post.assert_called_once()

    @patch('discord_sender.DISCORD_WEBHOOK_URL', 'https://discord.com/api/webhooks/123/456')
    @patch('discord_sender.requests.post')
    def test_send_to_discord_long_message(self, mock_post):
        """Test sending a long message"""
        # Mock the response
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        # Create a long message
        long_message = "Test message " * 100

        send_to_discord(long_message)

        # Should still send successfully
        mock_post.assert_called_once()
        payload = mock_post.call_args.kwargs['json']
        self.assertIn(payload['content'], long_message)

    @patch('discord_sender.DISCORD_WEBHOOK_URL', 'https://discord.com/api/webhooks/123/456')
    @patch('discord_sender.requests.post')
    def test_send_to_discord_payload_structure(self, mock_post):
        """Test the correct payload structure is sent"""
        # Mock the response
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        test_message = "Test message"
        send_to_discord(test_message)

        # Verify payload structure
        mock_post.assert_called_once()
        call_kwargs = mock_post.call_args.kwargs
        
        # Should have 'json' key with 'content'
        self.assertIn('json', call_kwargs)
        self.assertIn('content', call_kwargs['json'])
        self.assertEqual(call_kwargs['json']['content'], test_message)


if __name__ == '__main__':
    unittest.main()
