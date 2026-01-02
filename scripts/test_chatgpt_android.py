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


class TestEdgeCases:
    """Edge case tests."""

    def test_unicode_messages(self):
        from chatgpt_android import extract_messages
        xml = '''<hierarchy>
            <node text="This message contains émojis 🎉 and üñíçödé characters throughout" class="TextView"/>
        </hierarchy>'''
        messages = extract_messages(xml)
        assert len(messages) == 1
        assert "émojis" in messages[0]

    def test_very_long_message(self):
        from chatgpt_android import extract_messages
        long_text = "A" * 5000
        xml = f'<hierarchy><node text="{long_text}" class="TextView"/></hierarchy>'
        messages = extract_messages(xml)
        assert len(messages) == 1
        assert len(messages[0]) == 5000

    def test_multiple_messages_returns_all(self):
        from chatgpt_android import extract_messages
        xml = '''<hierarchy>
            <node text="First message that is long enough to pass the filter" class="TextView"/>
            <node text="Second message that is also long enough to pass filter" class="TextView"/>
            <node text="Third message with sufficient length for extraction" class="TextView"/>
        </hierarchy>'''
        messages = extract_messages(xml)
        assert len(messages) == 3

    def test_nested_quotes_in_text(self):
        from chatgpt_android import extract_messages
        # Text with escaped quotes shouldn't break regex
        xml = '''<hierarchy>
            <node text="He said &quot;hello&quot; and then left the room quickly" class="TextView"/>
        </hierarchy>'''
        messages = extract_messages(xml)
        assert len(messages) == 1
        assert '"hello"' in messages[0]

    def test_newlines_preserved(self):
        from chatgpt_android import extract_messages
        xml = '''<hierarchy>
            <node text="Line one&#10;Line two&#10;Line three is here for length" class="TextView"/>
        </hierarchy>'''
        messages = extract_messages(xml)
        assert len(messages) == 1
        assert messages[0].count('\n') == 2


class TestAppSwitching:
    """Tests for app switching logic."""

    @patch('time.sleep')
    @patch('chatgpt_android.run_rish')
    def test_switches_back_on_failure(self, mock_rish, mock_sleep):
        from chatgpt_android import dump_ui

        mock_rish.side_effect = [
            (True, ""),  # am start ChatGPT
            (False, "dump failed"),  # uiautomator fails
            (True, ""),  # am start Termux (should still be called)
        ]

        result = dump_ui()

        assert result == ""
        # Verify Termux was brought back
        assert mock_rish.call_count == 3
        last_call = mock_rish.call_args_list[-1]
        assert "termux" in str(last_call).lower()

    @patch('time.sleep')
    @patch('chatgpt_android.run_rish')
    def test_waits_for_app_switch(self, mock_rish, mock_sleep):
        from chatgpt_android import dump_ui

        mock_rish.return_value = (True, "<hierarchy></hierarchy>")

        dump_ui()

        # Should sleep after switching to ChatGPT
        mock_sleep.assert_called()


class TestCheckRish:
    """Tests for check_rish function."""

    @patch('chatgpt_android.os.path.exists')
    @patch('chatgpt_android.os.access')
    def test_returns_true_when_exists_and_executable(self, mock_access, mock_exists):
        from chatgpt_android import check_rish
        mock_exists.return_value = True
        mock_access.return_value = True

        assert check_rish() is True

    @patch('chatgpt_android.os.path.exists')
    def test_returns_false_when_not_exists(self, mock_exists):
        from chatgpt_android import check_rish
        mock_exists.return_value = False

        assert check_rish() is False

    @patch('chatgpt_android.os.path.exists')
    @patch('chatgpt_android.os.access')
    def test_returns_false_when_not_executable(self, mock_access, mock_exists):
        from chatgpt_android import check_rish
        mock_exists.return_value = True
        mock_access.return_value = False

        assert check_rish() is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
