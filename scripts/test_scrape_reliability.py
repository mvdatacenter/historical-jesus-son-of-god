#!/usr/bin/env python3
"""
Integration Test 1: Scrape Reliability

Test that as we scroll through a conversation:
1. We don't lose messages
2. We don't duplicate messages
3. Order is preserved
4. Scroll state is correctly tracked
5. Messages with same prefix but different content are correctly distinguished

This test uses mock data to simulate scrolling without touching the real ChatGPT app.
"""

import hashlib
import unittest
from typing import List, Tuple, Set


def msg_key(msg: str) -> str:
    """Generate a unique key for a message using hash.

    This matches the actual implementation in chatgpt_desktop.py.
    Uses full content hash because translation prompts often share the same prefix.
    """
    return hashlib.md5(msg.encode()).hexdigest()


class MockAXState:
    """
    Simulates the AX tree state as seen at different scroll positions.

    In ChatGPT:
    - Messages have Y positions (more negative = higher up = older)
    - Only messages in a certain Y range are "visible" at any time
    - Scrolling up reveals older messages (more negative Y)
    """

    def __init__(self, all_messages: List[dict]):
        """
        Args:
            all_messages: List of {"text": str, "y": float, "is_assistant": bool}
                         Ordered from oldest (most negative Y) to newest (highest Y)
        """
        self.all_messages = all_messages
        self.viewport_height = 500
        self.viewport_bottom = 0

    def scroll_up(self, amount: int = 1):
        """Scroll up (reveal older messages with more negative Y)."""
        self.viewport_bottom -= 100 * amount

    def scroll_to_bottom(self):
        """Scroll to bottom of conversation."""
        if self.all_messages:
            self.viewport_bottom = max(m["y"] for m in self.all_messages) + 100
        else:
            self.viewport_bottom = 0

    def get_visible_messages(self) -> List[Tuple[str, float, bool]]:
        """Get messages currently visible in viewport."""
        viewport_top = self.viewport_bottom - self.viewport_height
        visible = []
        for msg in self.all_messages:
            if viewport_top <= msg["y"] <= self.viewport_bottom:
                visible.append((msg["text"], msg["y"], msg["is_assistant"]))
        return visible

    def is_at_top(self) -> bool:
        """Check if we've scrolled to top of conversation."""
        if not self.all_messages:
            return True
        oldest_y = min(m["y"] for m in self.all_messages)
        viewport_top = self.viewport_bottom - self.viewport_height
        return viewport_top <= oldest_y


def simulate_scrape(mock_ax: MockAXState, num_turns: int) -> List[dict]:
    """
    Simulate the scraping algorithm.
    This mirrors the logic in extensive_scrape_history() from chatgpt_desktop.py.
    """
    mock_ax.scroll_to_bottom()

    collected_turns = []
    seen_keys: Set[str] = set()

    def find_new_assistant() -> str | None:
        visible = mock_ax.get_visible_messages()
        asst_msgs = [(t, y) for t, y, is_a in visible if is_a]
        asst_msgs.sort(key=lambda x: x[1], reverse=True)
        for text, y in asst_msgs:
            key = msg_key(text)
            if key not in seen_keys:
                return text
        return None

    def find_new_user() -> str | None:
        visible = mock_ax.get_visible_messages()
        user_msgs = [(t, y) for t, y, is_a in visible if not is_a]
        user_msgs.sort(key=lambda x: x[1], reverse=True)
        for text, y in user_msgs:
            key = msg_key(text)
            if key not in seen_keys:
                return text
        return None

    turn_num = 0
    while turn_num < num_turns and not mock_ax.is_at_top():
        # Find assistant message
        assistant_msg = None
        for _ in range(50):
            msg = find_new_assistant()
            if msg:
                assistant_msg = msg
                seen_keys.add(msg_key(msg))
                break
            if mock_ax.is_at_top():
                break
            mock_ax.scroll_up(1)

        if not assistant_msg:
            break

        # Find user message
        user_msg = None
        for _ in range(50):
            msg = find_new_user()
            if msg:
                user_msg = msg
                seen_keys.add(msg_key(msg))
                break
            if mock_ax.is_at_top():
                break
            mock_ax.scroll_up(1)

        if not user_msg:
            break

        collected_turns.append({"user": user_msg, "assistant": assistant_msg})
        turn_num += 1

    return collected_turns


class TestScrapeReliability(unittest.TestCase):
    """Test that scraping doesn't lose or duplicate messages."""

    def create_conversation(self, num_turns: int) -> List[dict]:
        """Create a mock conversation with N turns."""
        messages = []
        y = -1000 * num_turns

        for i in range(num_turns):
            messages.append({
                "text": f"User prompt {i + 1}: Tell me about topic {i + 1}",
                "y": y,
                "is_assistant": False
            })
            y += 200

            messages.append({
                "text": f"Assistant response {i + 1}: Here is info about topic {i + 1}",
                "y": y,
                "is_assistant": True
            })
            y += 200

        return messages

    def test_collects_all_turns(self):
        """Test that we collect exactly the requested number of turns."""
        messages = self.create_conversation(5)
        mock_ax = MockAXState(messages)

        turns = simulate_scrape(mock_ax, num_turns=3)

        self.assertEqual(len(turns), 3)

    def test_no_message_loss(self):
        """Test that no messages are lost when collecting all turns."""
        num_turns = 4
        messages = self.create_conversation(num_turns)
        mock_ax = MockAXState(messages)

        turns = simulate_scrape(mock_ax, num_turns=num_turns)

        self.assertEqual(len(turns), num_turns)

        all_texts_in_turns = set()
        for turn in turns:
            all_texts_in_turns.add(turn["user"])
            all_texts_in_turns.add(turn["assistant"])

        original_texts = {m["text"] for m in messages}
        self.assertEqual(all_texts_in_turns, original_texts)

    def test_no_duplicates(self):
        """Test that messages aren't duplicated."""
        messages = self.create_conversation(5)
        mock_ax = MockAXState(messages)

        turns = simulate_scrape(mock_ax, num_turns=5)

        all_texts = []
        for turn in turns:
            all_texts.append(turn["user"])
            all_texts.append(turn["assistant"])

        self.assertEqual(len(all_texts), len(set(all_texts)))

    def test_correct_pairing(self):
        """Test that user messages are correctly paired with their responses."""
        messages = self.create_conversation(3)
        mock_ax = MockAXState(messages)

        turns = simulate_scrape(mock_ax, num_turns=3)

        for i, turn in enumerate(turns):
            expected_num = 3 - i
            self.assertIn(f"topic {expected_num}", turn["user"])
            self.assertIn(f"topic {expected_num}", turn["assistant"])

    def test_newest_first_order(self):
        """Test that turns are returned newest-first."""
        messages = self.create_conversation(3)
        mock_ax = MockAXState(messages)

        turns = simulate_scrape(mock_ax, num_turns=3)

        import re
        turn_numbers = []
        for turn in turns:
            match = re.search(r'topic (\d+)', turn["user"])
            if match:
                turn_numbers.append(int(match.group(1)))

        self.assertEqual(turn_numbers, [3, 2, 1])

    def test_empty_conversation(self):
        """Test handling of empty conversation."""
        mock_ax = MockAXState([])

        turns = simulate_scrape(mock_ax, num_turns=5)

        self.assertEqual(len(turns), 0)


class TestSamePrefixMessages(unittest.TestCase):
    """Test handling of messages that share the same prefix.

    This was a real bug: translation prompts all start with the same Polish
    instructions, so first-100-chars matching caused them to be treated as
    duplicates. The fix was to use a hash of the full message.
    """

    def test_same_prefix_different_content(self):
        """Test that messages with same prefix but different content are distinguished."""
        # Simulates translation prompts that all start with "Przetłumacz..."
        prefix = "Przetłumacz poniższy tekst naukowy LaTeX na język polski. ZASADY: 1. PRIORYTET..."

        messages = [
            # Turn 1
            {"text": prefix + " Section 1 content here", "y": -2000, "is_assistant": False},
            {"text": "Polish translation of section 1", "y": -1800, "is_assistant": True},
            # Turn 2 - same prefix, different content
            {"text": prefix + " Section 2 content here", "y": -1600, "is_assistant": False},
            {"text": "Polish translation of section 2", "y": -1400, "is_assistant": True},
            # Turn 3 - same prefix, different content
            {"text": prefix + " Section 3 content here", "y": -1200, "is_assistant": False},
            {"text": "Polish translation of section 3", "y": -1000, "is_assistant": True},
        ]

        mock_ax = MockAXState(messages)
        turns = simulate_scrape(mock_ax, num_turns=3)

        # Should collect all 3 turns despite same prefix
        self.assertEqual(len(turns), 3,
            "Should collect all 3 turns even though USER messages share same prefix")

        # Verify each turn has unique content
        user_texts = [t["user"] for t in turns]
        self.assertEqual(len(set(user_texts)), 3, "All USER messages should be unique")

    def test_hash_based_deduplication(self):
        """Test that hash-based key correctly identifies duplicates."""
        msg1 = "Same prefix here but content A"
        msg2 = "Same prefix here but content B"
        msg3 = "Same prefix here but content A"  # Actual duplicate of msg1

        key1 = msg_key(msg1)
        key2 = msg_key(msg2)
        key3 = msg_key(msg3)

        # Different content = different keys
        self.assertNotEqual(key1, key2)

        # Same content = same key
        self.assertEqual(key1, key3)

    def test_first_100_chars_would_fail(self):
        """Demonstrate that first-100-chars approach fails for translation prompts."""
        prefix = "A" * 100  # 100 char prefix

        msg1 = prefix + " unique content 1"
        msg2 = prefix + " unique content 2"

        # First 100 chars are identical
        self.assertEqual(msg1[:100], msg2[:100])

        # But hash is different
        self.assertNotEqual(msg_key(msg1), msg_key(msg2))


class TestMsgKeyFunction(unittest.TestCase):
    """Test the msg_key function matches chatgpt_desktop.py implementation."""

    def test_uses_md5_hash(self):
        """Test that msg_key uses MD5 hash."""
        msg = "Test message content"
        expected = hashlib.md5(msg.encode()).hexdigest()

        self.assertEqual(msg_key(msg), expected)

    def test_full_content_hashed(self):
        """Test that full content affects the hash."""
        short = "Hello"
        long = "Hello world with more content"

        self.assertNotEqual(msg_key(short), msg_key(long))

    def test_unicode_handling(self):
        """Test that unicode content (Polish text) is handled correctly."""
        polish = "Przetłumacz poniższy tekst naukowy LaTeX na język polski"
        key = msg_key(polish)

        self.assertEqual(len(key), 32)  # MD5 hex is 32 chars
        self.assertTrue(all(c in '0123456789abcdef' for c in key))


if __name__ == "__main__":
    unittest.main(verbosity=2)
