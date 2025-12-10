#!/usr/bin/env python3
"""
Integration Test 2: AX Tree Parsing

Tests the ACTUAL parsing functions from chatgpt_desktop.py with mocked AX elements.
The mock elements simulate the real AX tree structure from ChatGPT.
"""

import json
import os
import sys
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.dirname(__file__))

from ApplicationServices import (
    kAXRoleAttribute,
    kAXDescriptionAttribute,
    kAXChildrenAttribute,
    kAXPositionAttribute,
)


def create_mock_ax_tree(fixture_data: dict) -> MagicMock:
    """
    Create a mock AX element tree from fixture data.
    This simulates what the real AX API returns.
    """
    def create_element(data: dict) -> MagicMock:
        element = MagicMock()
        element._test_data = data  # For debugging

        def get_attr(attr_name):
            if attr_name == kAXRoleAttribute:
                return data.get("role")
            elif attr_name == "AXSubrole":
                return data.get("subrole")
            elif attr_name == kAXDescriptionAttribute:
                return data.get("desc")
            elif attr_name == "AXValue":
                return data.get("value")
            elif attr_name == kAXPositionAttribute:
                if "x" in data and "y" in data:
                    # Return a mock position object that str() gives "x:N y:N"
                    pos = MagicMock()
                    pos.__str__ = lambda self: f"x:{data['x']} y:{data['y']}"
                    return pos
                return None
            elif attr_name == kAXChildrenAttribute:
                children = data.get("children", [])
                return [create_element(c) for c in children]
            return None

        element.get_attr = get_attr
        return element

    return create_element(fixture_data)


def mock_ax_attr(element, attr_name):
    """Mock implementation of ax_attr that uses our test data."""
    return element.get_attr(attr_name)


class TestCollectMessagesWithPosition(unittest.TestCase):
    """Test collect_messages_with_position with mock AX tree."""

    def setUp(self):
        """Create a mock conversation tree."""
        # Simulates the conversation section of ChatGPT's AX tree
        self.mock_tree = {
            "role": "AXList",
            "subrole": "AXSectionList",
            "children": [
                # Empty group (header)
                {"role": "AXGroup", "subrole": None, "children": []},
                # USER message (X=845 = right side)
                {
                    "role": "AXGroup",
                    "subrole": None,
                    "x": 251.0,
                    "y": -2000.0,
                    "children": [{
                        "role": "AXGroup",
                        "subrole": "AXHostingView",
                        "x": 251.0,
                        "y": -2000.0,
                        "children": [{
                            "role": "AXStaticText",
                            "x": 845.5,
                            "y": -1990.0,
                            "desc": "Translate this text to Polish please"
                        }]
                    }]
                },
                # ASSISTANT message (X=509 = left side)
                {
                    "role": "AXGroup",
                    "subrole": None,
                    "x": 251.0,
                    "y": -1500.0,
                    "children": [{
                        "role": "AXGroup",
                        "subrole": "AXHostingView",
                        "x": 251.0,
                        "y": -1500.0,
                        "children": [{
                            "role": "AXStaticText",
                            "x": 509.5,
                            "y": -1490.0,
                            "desc": "Proszę przetłumaczyć ten tekst na polski"
                        }]
                    }]
                },
                # Thinking indicator (has value, not desc - should be ignored)
                {
                    "role": "AXGroup",
                    "subrole": None,
                    "children": [{
                        "role": "AXGroup",
                        "subrole": "AXHostingView",
                        "children": [{
                            "role": "AXStaticText",
                            "x": 509.5,
                            "y": -1400.0,
                            "value": "Thought for a couple of seconds"
                            # No desc!
                        }]
                    }]
                },
            ]
        }

    def test_extracts_messages_with_correct_roles(self):
        """Test that messages are extracted with correct USER/ASSISTANT roles."""
        from chatgpt_desktop import collect_messages_with_position

        mock_element = create_mock_ax_tree(self.mock_tree)
        messages = []

        with patch('chatgpt_desktop.ax_attr', side_effect=mock_ax_attr):
            collect_messages_with_position(mock_element, messages)

        # Should have 2 messages (thinking indicator filtered out)
        self.assertEqual(len(messages), 2, f"Expected 2 messages, got {len(messages)}")

        # Check roles - USER has X >= 700, ASSISTANT has X < 700
        user_msgs = [m for m in messages if not m[2]]  # is_assistant = False
        asst_msgs = [m for m in messages if m[2]]       # is_assistant = True

        self.assertEqual(len(user_msgs), 1, "Should have 1 USER message")
        self.assertEqual(len(asst_msgs), 1, "Should have 1 ASSISTANT message")

    def test_thinking_indicator_not_collected(self):
        """Test that 'Thought for...' message is NOT collected."""
        from chatgpt_desktop import collect_messages_with_position

        mock_element = create_mock_ax_tree(self.mock_tree)
        messages = []

        with patch('chatgpt_desktop.ax_attr', side_effect=mock_ax_attr):
            collect_messages_with_position(mock_element, messages)

        # Check that thinking indicator is not in results
        for text, y, is_asst in messages:
            self.assertNotIn("Thought for", text,
                           "Thinking indicator should not be collected")

    def test_message_content_correct(self):
        """Test that message content is correctly extracted."""
        from chatgpt_desktop import collect_messages_with_position

        mock_element = create_mock_ax_tree(self.mock_tree)
        messages = []

        with patch('chatgpt_desktop.ax_attr', side_effect=mock_ax_attr):
            collect_messages_with_position(mock_element, messages)

        texts = [m[0] for m in messages]
        self.assertIn("Translate this text to Polish please", texts)
        self.assertIn("Proszę przetłumaczyć ten tekst na polski", texts)


class TestCollectAllTextFromElement(unittest.TestCase):
    """Test collect_all_text_from_element function."""

    def test_only_collects_desc_not_value(self):
        """Test that only desc attribute is collected, not value."""
        from chatgpt_desktop import collect_all_text_from_element

        # Element with both desc and value
        mock_data = {
            "role": "AXStaticText",
            "desc": "This is description",
            "value": "This is value - SHOULD NOT APPEAR",
            "children": []
        }
        mock_element = create_mock_ax_tree(mock_data)

        texts = []
        with patch('chatgpt_desktop.ax_attr', side_effect=mock_ax_attr):
            collect_all_text_from_element(mock_element, texts)

        self.assertEqual(len(texts), 1)
        self.assertEqual(texts[0], "This is description")

    def test_skips_elements_without_desc(self):
        """Test that elements without desc are skipped."""
        from chatgpt_desktop import collect_all_text_from_element

        mock_data = {
            "role": "AXStaticText",
            "value": "Only value, no desc",
            "children": []
        }
        mock_element = create_mock_ax_tree(mock_data)

        texts = []
        with patch('chatgpt_desktop.ax_attr', side_effect=mock_ax_attr):
            collect_all_text_from_element(mock_element, texts)

        self.assertEqual(len(texts), 0, "Should not collect text without desc")


class TestCollectAllVisibleMessages(unittest.TestCase):
    """Test collect_all_visible_messages function."""

    def test_filters_short_messages(self):
        """Test that messages <= 20 chars are filtered out."""
        from chatgpt_desktop import collect_all_visible_messages

        mock_tree = {
            "role": "AXList",
            "children": [
                {
                    "role": "AXGroup",
                    "children": [{
                        "role": "AXStaticText",
                        "x": 509.5,
                        "y": -100.0,
                        "desc": "Short"  # 5 chars - should be filtered
                    }]
                },
                {
                    "role": "AXGroup",
                    "children": [{
                        "role": "AXStaticText",
                        "x": 509.5,
                        "y": -200.0,
                        "desc": "This is a longer message that passes the filter"
                    }]
                }
            ]
        }

        mock_element = create_mock_ax_tree(mock_tree)

        with patch('chatgpt_desktop.ax_attr', side_effect=mock_ax_attr):
            messages = collect_all_visible_messages(mock_element)

        # Should only have the long message
        self.assertEqual(len(messages), 1)
        self.assertIn("longer message", messages[0][0])

    def test_filters_ui_keywords(self):
        """Test that UI keywords like 'Search', 'ChatGPT' are filtered."""
        from chatgpt_desktop import collect_all_visible_messages

        mock_tree = {
            "role": "AXList",
            "children": [
                {
                    "role": "AXGroup",
                    "children": [{
                        "role": "AXStaticText",
                        "x": 509.5,
                        "y": -100.0,
                        "desc": "Search for conversations here"  # Starts with "Search"
                    }]
                },
                {
                    "role": "AXGroup",
                    "children": [{
                        "role": "AXStaticText",
                        "x": 509.5,
                        "y": -200.0,
                        "desc": "Actual message content here"
                    }]
                }
            ]
        }

        mock_element = create_mock_ax_tree(mock_tree)

        with patch('chatgpt_desktop.ax_attr', side_effect=mock_ax_attr):
            messages = collect_all_visible_messages(mock_element)

        # Should only have the actual message
        self.assertEqual(len(messages), 1)
        self.assertIn("Actual message", messages[0][0])


class TestFixtureIntegration(unittest.TestCase):
    """Test with the full fixture file."""

    @classmethod
    def setUpClass(cls):
        fixture_path = os.path.join(
            os.path.dirname(__file__),
            "test_fixtures",
            "sample_conversation.json"
        )
        with open(fixture_path) as f:
            cls.fixture = json.load(f)

    def test_fixture_messages_parse_correctly(self):
        """Test that fixture messages parse to expected turns."""
        # Build a mock tree from fixture
        mock_tree = {
            "role": "AXList",
            "subrole": "AXSectionList",
            "children": self.fixture["messages"]
        }

        from chatgpt_desktop import collect_messages_with_position

        mock_element = create_mock_ax_tree(mock_tree)
        messages = []

        with patch('chatgpt_desktop.ax_attr', side_effect=mock_ax_attr):
            collect_messages_with_position(mock_element, messages)

        # Should have 4 messages (2 user + 2 assistant)
        self.assertEqual(len(messages), 4)

        # Check correct role assignment
        user_msgs = [m for m in messages if not m[2]]
        asst_msgs = [m for m in messages if m[2]]

        self.assertEqual(len(user_msgs), 2)
        self.assertEqual(len(asst_msgs), 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
