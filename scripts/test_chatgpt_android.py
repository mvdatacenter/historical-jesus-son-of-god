#!/usr/bin/env python3
"""Tests for chatgpt_android.py"""

import pytest
from unittest.mock import patch, MagicMock

# Sample UI XML from ChatGPT app
SAMPLE_XML = '''<?xml version='1.0' encoding='UTF-8'?>
<hierarchy rotation="0">
  <node text="" class="android.widget.FrameLayout" package="com.openai.chatgpt">
    <node text="Hello, how can I help?" class="android.widget.TextView" bounds="[0,100][500,200]"/>
    <node text="What is 2+2?" class="android.widget.TextView" bounds="[600,300][1000,400]"/>
    <node text="2+2 equals 4. This is a basic arithmetic operation." class="android.widget.TextView" bounds="[0,500][500,700]"/>
    <node text="ChatGPT" class="android.widget.TextView" bounds="[0,0][100,50]"/>
    <node text="New chat" class="android.widget.Button" bounds="[0,0][100,50]"/>
  </node>
</hierarchy>
'''

SAMPLE_XML_WITH_ENTITIES = '''<?xml version='1.0' encoding='UTF-8'?>
<hierarchy rotation="0">
  <node text="Line 1&#10;Line 2&#10;Line 3 is a longer line with more content" class="android.widget.TextView" bounds="[0,100][500,200]"/>
</hierarchy>
'''


class TestExtractMessages:
    """Tests for extract_messages function."""

    def test_extracts_long_messages(self):
        from chatgpt_android import extract_messages
        messages = extract_messages(SAMPLE_XML)
        # Should get the long message (30+ chars), not short ones or UI elements
        assert len(messages) == 1
        assert "2+2 equals 4" in messages[0]

    def test_skips_ui_elements(self):
        from chatgpt_android import extract_messages
        messages = extract_messages(SAMPLE_XML)
        # Should not include "ChatGPT" or "New chat"
        for msg in messages:
            assert "chatgpt" not in msg.lower()
            assert "new chat" not in msg.lower()

    def test_decodes_html_entities(self):
        from chatgpt_android import extract_messages
        messages = extract_messages(SAMPLE_XML_WITH_ENTITIES)
        assert len(messages) == 1
        # &#10; should be decoded to newline
        assert "\n" in messages[0]

    def test_empty_xml(self):
        from chatgpt_android import extract_messages
        messages = extract_messages("")
        assert messages == []

    def test_no_text_nodes(self):
        from chatgpt_android import extract_messages
        xml = '<hierarchy><node class="Button"/></hierarchy>'
        messages = extract_messages(xml)
        assert messages == []


class TestRunRish:
    """Tests for run_rish function."""

    @patch('chatgpt_android.subprocess.run')
    @patch('chatgpt_android.check_rish', return_value=True)
    def test_successful_command(self, mock_check, mock_run):
        from chatgpt_android import run_rish
        mock_run.return_value = MagicMock(returncode=0, stdout="uid=2000(shell)")

        success, output = run_rish("id")

        assert success is True
        assert "shell" in output

    @patch('chatgpt_android.subprocess.run')
    @patch('chatgpt_android.check_rish', return_value=True)
    def test_failed_command(self, mock_check, mock_run):
        from chatgpt_android import run_rish
        mock_run.return_value = MagicMock(returncode=1, stdout="error")

        success, output = run_rish("bad_command")

        assert success is False

    @patch('chatgpt_android.check_rish', return_value=False)
    def test_rish_not_found(self, mock_check):
        from chatgpt_android import run_rish

        success, output = run_rish("id")

        assert success is False
        assert "not found" in output


class TestDumpUI:
    """Tests for dump_ui function."""

    @patch('chatgpt_android.run_rish')
    def test_dumps_and_returns_content(self, mock_rish):
        from chatgpt_android import dump_ui

        # Mock the sequence of calls
        mock_rish.side_effect = [
            (True, ""),  # am start ChatGPT
            (True, "UI dumped"),  # uiautomator dump
            (True, SAMPLE_XML),  # cat file
            (True, ""),  # am start Termux
            (True, ""),  # rm file
        ]

        content = dump_ui()

        assert "hierarchy" in content
        assert mock_rish.call_count == 5

    @patch('chatgpt_android.run_rish')
    def test_returns_empty_on_dump_failure(self, mock_rish):
        from chatgpt_android import dump_ui

        mock_rish.side_effect = [
            (True, ""),  # am start ChatGPT
            (False, "error"),  # uiautomator dump fails
            (True, ""),  # am start Termux (cleanup)
        ]

        content = dump_ui()

        assert content == ""


class TestReadLatest:
    """Tests for read_latest function."""

    @patch('chatgpt_android.dump_ui')
    @patch('chatgpt_android.check_rish', return_value=True)
    def test_returns_last_message(self, mock_check, mock_dump):
        from chatgpt_android import read_latest
        mock_dump.return_value = SAMPLE_XML

        result = read_latest()

        assert "2+2 equals 4" in result

    @patch('chatgpt_android.dump_ui')
    @patch('chatgpt_android.check_rish', return_value=True)
    def test_returns_empty_when_no_messages(self, mock_check, mock_dump):
        from chatgpt_android import read_latest
        mock_dump.return_value = '<hierarchy></hierarchy>'

        result = read_latest()

        assert result == ""


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
