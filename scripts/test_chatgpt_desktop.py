#!/usr/bin/env python3
"""
Tests for chatgpt_desktop.py

These tests verify fixes for specific bugs. Each test would FAIL
if the corresponding bug was reintroduced.

Run with: poetry run python scripts/test_chatgpt_desktop.py
"""

import sys
import re
sys.path.insert(0, 'scripts')

import chatgpt_desktop
from chatgpt_desktop import collect_messages_with_position, collect_all_visible_messages


class MockPosition:
    """Mock AXPosition value."""
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return f"x:{self.x} y:{self.y}"


class MockAXElement:
    """Mock AXUIElement for testing."""
    def __init__(self, role=None, value=None, description=None, position=None, children=None, subrole=None):
        self.attrs = {
            "AXRole": role,
            "AXValue": value,
            "AXDescription": description,
            "AXPosition": position,
            "AXChildren": children or [],
            "AXSubrole": subrole,
        }

    def __iter__(self):
        return iter(self.attrs.get("AXChildren", []))


_original_ax_attr = chatgpt_desktop.ax_attr

def mock_ax_attr(element, attr_name):
    if isinstance(element, MockAXElement):
        return element.attrs.get(attr_name)
    return _original_ax_attr(element, attr_name)

chatgpt_desktop.ax_attr = mock_ax_attr


def build_tree(messages):
    """Build mock AX tree from (text, y_pos, is_assistant) tuples."""
    containers = []
    for text, y_pos, is_assistant in messages:
        text_el = MockAXElement(role="AXStaticText", value=text)
        group = MockAXElement(
            role="AXGroup",
            position=MockPosition(251, y_pos),
            children=[text_el],
            subrole="AXHostingView" if is_assistant else None,
        )
        containers.append(group)
    return MockAXElement(role="AXScrollArea", children=containers)


# =============================================================================
# BUG FIX #1: Negative Y coordinate regex
#
# OLD BUG: Pattern was y:([\d.]+) which only matched positive numbers.
# When content scrolled up, Y became negative and messages were lost.
# FIX: Pattern is now y:(-?[\d.]+)
# =============================================================================

def test_bug1_negative_y_must_be_parsed():
    r"""
    BUG #1: Regex must parse negative Y values.

    OLD CODE: r'y:([\d.]+)' - FAILS on negative Y
    NEW CODE: r'y:(-?[\d.]+)' - handles negative Y

    This test uses Y=-1500 which the old regex would NOT match,
    causing the message to be silently dropped.
    """
    tree = build_tree([
        ("Message at Y=-1500 must be found", -1500, False),
        ("Message at Y=-100 near bottom", -100, True),
    ])

    result = collect_all_visible_messages(tree)

    # OLD BUG: Would return only 1 message (the Y=-100 one)
    # FIXED: Returns both messages
    assert len(result) == 2, (
        f"BUG #1 REGRESSION: Only got {len(result)} messages!\n"
        f"The Y=-1500 message was lost because regex doesn't match negative Y.\n"
        f"Fix: Change y:([\\d.]+) to y:(-?[\\d.]+)"
    )

    # Verify the negative Y was actually parsed correctly
    assert result[0][1] == -1500, (
        f"Y position should be -1500, got {result[0][1]}\n"
        f"Regex is not parsing negative numbers correctly."
    )

    print("✓ BUG #1 FIXED: Negative Y values parsed correctly")


def test_bug1_very_negative_y():
    """
    BUG #1 variant: Extremely negative Y (long conversation scrolled up).
    """
    tree = build_tree([
        ("Ancient message from start of chat", -50000, False),
        ("Recent message visible on screen", -100, True),
    ])

    result = collect_all_visible_messages(tree)

    assert len(result) == 2, (
        f"BUG #1 REGRESSION: Lost message at Y=-50000\n"
        f"Got {len(result)} messages instead of 2"
    )
    assert result[0][1] == -50000

    print("✓ BUG #1 FIXED: Very negative Y (-50000) handled")


# =============================================================================
# BUG FIX #2: Length-based role detection removed
#
# OLD BUG: Code had `is_user = len(msg) < 100` to guess user vs assistant.
# This caused long user prompts (>100 chars) to be classified as "assistant".
# When getting "latest assistant response", user's own prompt was returned.
#
# FIX: Removed all role detection. Messages sorted by Y position only.
# =============================================================================

def test_bug2_long_user_prompt_not_returned_as_response():
    """
    BUG #2: Long user message must NOT be returned as "latest response".

    OLD CODE: is_user = len(msg) < 100
    This meant a 500-char user prompt was classified as "assistant"
    and returned when asking for the latest response.

    SCENARIO: User pastes a long prompt, ChatGPT gives short reply.
    OLD BUG: Returns the user's own prompt as the "response".
    FIXED: Returns the actual assistant response (by Y position).
    """
    # User's long prompt (500+ chars) - would be is_user=False with old code!
    long_prompt = """Please analyze the following code and explain what it does:

def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

for i in range(10):
    print(fibonacci(i))

I need to understand the time complexity and suggest optimizations.
Also explain the recursive call stack for fibonacci(5)."""

    # Assistant's short response (50 chars) - would be is_user=True with old code!
    short_response = "This code calculates Fibonacci numbers recursively."

    assert len(long_prompt) > 100, "Test setup: prompt must be >100 chars"
    assert len(short_response) < 100, "Test setup: response must be <100 chars"

    tree = build_tree([
        (long_prompt, -200, False),    # User prompt at Y=-200
        (short_response, -100, True),  # Assistant response at Y=-100 (latest)
    ])

    result = collect_all_visible_messages(tree)

    # The latest message (highest Y = -100) should be the short response
    latest = result[-1][0]

    assert latest == short_response, (
        f"BUG #2 REGRESSION: Latest message is the user's prompt, not the response!\n"
        f"This happens when code uses `is_user = len(msg) < 100`.\n"
        f"Expected: {short_response!r}\n"
        f"Got: {latest[:60]!r}...\n"
        f"Fix: Remove all length-based role detection."
    )

    print("✓ BUG #2 FIXED: Long user prompt not returned as response")


def test_bug2_extreme_length_difference():
    """
    BUG #2 variant: 2000-char user prompt, 10-char assistant response.

    With is_user = len(msg) < 100:
    - 2000-char prompt -> is_user=False (WRONG - it's user!)
    - 10-char response -> is_user=True (WRONG - it's assistant!)

    Result: Everything backwards.
    """
    huge_prompt = "Explain this: " + ("x" * 2000)  # 2014 chars
    tiny_response = "Sure, I will explain this for you."  # 35 chars

    tree = build_tree([
        (huge_prompt, -200, False),
        (tiny_response, -100, True),
    ])

    result = collect_all_visible_messages(tree)
    latest = result[-1][0]

    assert latest == tiny_response, (
        f"BUG #2 REGRESSION: 2000-char user message returned as 'response'!\n"
        f"Got: {latest[:50]!r}..."
    )

    print("✓ BUG #2 FIXED: Extreme length difference handled")


def test_bug2_multiple_long_user_messages():
    """
    BUG #2 variant: Conversation with multiple long user messages.

    If length heuristic exists, ALL long messages get classified wrong.
    """
    tree = build_tree([
        ("First long user question about programming" * 5, -400, False),   # 215 chars
        ("Short answer from the AI assistant.", -350, True),               # 35 chars
        ("Second even longer user question" * 10, -300, False),            # 320 chars
        ("Another brief response from assistant.", -250, True),            # 39 chars
        ("Third massive user prompt with code" * 8, -200, False),          # 280 chars
        ("Final short assistant response here.", -100, True),              # 36 chars
    ])

    result = collect_all_visible_messages(tree)

    # Latest (Y=-100) must be "Final short assistant response"
    latest = result[-1][0]
    assert "Final short" in latest, (
        f"BUG #2 REGRESSION: Latest is not the final response!\n"
        f"Got: {latest[:50]!r}..."
    )

    # Check ordering is by Y, not by some role-based logic
    assert result[0][1] == -400  # First message has lowest Y
    assert result[-1][1] == -100  # Last message has highest Y

    print("✓ BUG #2 FIXED: Multiple long user messages handled")


# =============================================================================
# Combined scenario: Both bugs together
# =============================================================================

def test_both_bugs_negative_y_and_long_prompt():
    """
    Combined: Negative Y + long user prompt.

    This test would fail if EITHER bug is present.
    """
    long_prompt = "Detailed question: " + ("explain " * 50)  # 450+ chars

    tree = build_tree([
        (long_prompt, -5000, False),                           # Far up, long
        ("Short reply from the assistant.", -4900, True),      # Far up, short
        ("Another long question here" * 10, -200, False),      # Near bottom, long
        ("The final response is this.", -100, True),           # Bottom, short
    ])

    result = collect_all_visible_messages(tree)

    # Must have all 4 messages (bug #1 would lose the Y=-5000 ones)
    assert len(result) == 4, (
        f"Lost messages! Got {len(result)}, expected 4.\n"
        f"Bug #1 (negative Y regex) may be present."
    )

    # Latest must be "The final response" (bug #2 would return the long prompt)
    assert "final response" in result[-1][0], (
        f"Wrong latest message!\n"
        f"Bug #2 (length heuristic) may be present.\n"
        f"Got: {result[-1][0][:50]!r}..."
    )

    # Verify Y ordering
    ys = [y for _, y in result]
    assert ys == sorted(ys), f"Messages not sorted by Y: {ys}"

    print("✓ BOTH BUGS FIXED: Negative Y + long prompt handled")


def run_all_tests():
    tests = [
        test_bug1_negative_y_must_be_parsed,
        test_bug1_very_negative_y,
        test_bug2_long_user_prompt_not_returned_as_response,
        test_bug2_extreme_length_difference,
        test_bug2_multiple_long_user_messages,
        test_both_bugs_negative_y_and_long_prompt,
    ]

    print("=" * 60)
    print("chatgpt_desktop.py - Bug Regression Tests")
    print("=" * 60)
    print("These tests FAIL if old bugs are reintroduced.\n")

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"✗ FAILED: {test.__name__}")
            print(f"  {e}\n")
            failed += 1
        except Exception as e:
            print(f"✗ ERROR: {test.__name__}")
            print(f"  {type(e).__name__}: {e}\n")
            failed += 1

    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)

    return failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
