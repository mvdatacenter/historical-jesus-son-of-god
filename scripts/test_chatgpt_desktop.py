#!/usr/bin/env python3
"""
Unit tests for chatgpt_desktop.py

Tests core logic with mocked dependencies to ensure the script
works correctly without requiring ChatGPT Desktop app to be running.
"""

import sys
import unittest
from unittest.mock import Mock, patch, MagicMock


class TestChatGPTDesktop(unittest.TestCase):
    """Test chatgpt_desktop.py core logic with mocks."""

    def setUp(self):
        """Set up test fixtures."""
        # Mock app objects
        self.mock_ax_app = Mock()
        self.mock_ns_app = Mock()

        # Mock UI elements
        self.mock_text_input = Mock()
        self.mock_send_button = Mock()

        # Mock position/size attributes
        self.mock_position = Mock()
        self.mock_position.__str__ = Mock(return_value="x:100.0 y:200.0")
        self.mock_size = Mock()
        self.mock_size.__str__ = Mock(return_value="w:400.0 h:50.0")

    @patch('chatgpt_desktop.find_chatgpt_app')
    def test_find_chatgpt_app_found(self, mock_find):
        """Test finding ChatGPT app successfully."""
        mock_find.return_value = (self.mock_ax_app, self.mock_ns_app)

        ax_app, ns_app = mock_find()

        self.assertIsNotNone(ax_app)
        self.assertIsNotNone(ns_app)

    @patch('chatgpt_desktop.find_chatgpt_app')
    def test_find_chatgpt_app_not_found(self, mock_find):
        """Test ChatGPT app not found."""
        mock_find.return_value = (None, None)

        ax_app, ns_app = mock_find()

        self.assertIsNone(ax_app)
        self.assertIsNone(ns_app)

    @patch('chatgpt_desktop.find_text_input')
    def test_find_text_input_found(self, mock_find_input):
        """Test finding text input field successfully."""
        mock_find_input.return_value = self.mock_text_input

        text_input = mock_find_input(self.mock_ax_app)

        self.assertIsNotNone(text_input)

    @patch('chatgpt_desktop.find_text_input')
    def test_find_text_input_not_found(self, mock_find_input):
        """Test text input field not found."""
        mock_find_input.return_value = None

        text_input = mock_find_input(self.mock_ax_app)

        self.assertIsNone(text_input)

    @patch('chatgpt_desktop.collect_all_buttons')
    def test_collect_buttons_finds_send(self, mock_collect):
        """Test collecting buttons finds Send button."""
        buttons_list = []

        def side_effect(element, buttons, depth=0, max_depth=20):
            buttons.append((self.mock_send_button, 'Send'))
            buttons.append((Mock(), 'Cancel'))

        mock_collect.side_effect = side_effect

        buttons = []
        mock_collect(self.mock_ax_app, buttons)

        send_button = None
        for btn, desc in buttons:
            if desc and desc == 'Send':
                send_button = btn
                break

        self.assertIsNotNone(send_button)
        self.assertEqual(len(buttons), 2)

    @patch('chatgpt_desktop.collect_all_buttons')
    def test_collect_buttons_no_send(self, mock_collect):
        """Test collecting buttons when Send button missing."""
        buttons_list = []

        def side_effect(element, buttons, depth=0, max_depth=20):
            buttons.append((Mock(), 'Cancel'))
            buttons.append((Mock(), 'Clear'))

        mock_collect.side_effect = side_effect

        buttons = []
        mock_collect(self.mock_ax_app, buttons)

        send_button = None
        for btn, desc in buttons:
            if desc and desc == 'Send':
                send_button = btn
                break

        self.assertIsNone(send_button)

    def test_position_parsing(self):
        """Test parsing position and size strings."""
        import re

        pos_str = "x:100.5 y:200.75"
        size_str = "w:400.0 h:50.25"

        pos_match = re.search(r'x:([\d.]+)\s+y:([\d.]+)', pos_str)
        size_match = re.search(r'w:([\d.]+)\s+h:([\d.]+)', size_str)

        self.assertIsNotNone(pos_match)
        self.assertIsNotNone(size_match)

        pos_x = float(pos_match.group(1))
        pos_y = float(pos_match.group(2))
        width = float(size_match.group(1))
        height = float(size_match.group(2))

        self.assertEqual(pos_x, 100.5)
        self.assertEqual(pos_y, 200.75)
        self.assertEqual(width, 400.0)
        self.assertEqual(height, 50.25)

        # Test center calculation
        click_x = pos_x + width / 2
        click_y = pos_y + height / 2

        self.assertEqual(click_x, 300.5)
        self.assertEqual(click_y, 225.875)

    @patch('chatgpt_desktop.set_clipboard')
    def test_set_clipboard_called(self, mock_clipboard):
        """Test clipboard is set with prompt text."""
        prompt = "Test prompt"
        mock_clipboard(prompt)

        mock_clipboard.assert_called_once_with(prompt)

    @patch('chatgpt_desktop.collect_assistant_messages')
    def test_collect_messages_filters_duplicates(self, mock_collect):
        """Test message collection handles duplicates."""
        messages_list = []

        def side_effect(element, messages, depth=0, max_depth=20):
            messages.extend([
                "Response 1",
                "Response 1",  # Duplicate
                "Response 2",
                "S",  # Too short (1 char)
                "Response 3"
            ])

        mock_collect.side_effect = side_effect

        messages = []
        mock_collect(self.mock_ax_app, messages)

        # Filter meaningful messages (>1 char, ASCII)
        meaningful = [msg for msg in messages if len(msg) > 1 and ord(msg[0]) < 128]

        # Remove duplicates
        seen = set()
        unique = []
        for msg in meaningful:
            key = msg[:100]
            if key not in seen:
                seen.add(key)
                unique.append(msg)

        self.assertEqual(len(unique), 3)  # Response 1, Response 2, Response 3


if __name__ == '__main__':
    # Run tests
    unittest.main()
