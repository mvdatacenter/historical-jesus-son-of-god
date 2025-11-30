#!/usr/bin/env python3
"""
chatgpt_desktop.py

Automate ChatGPT Desktop App via macOS Accessibility API.

Features:
  - `send` sends a prompt to ChatGPT and waits for response
  - `read` reads the text of the last assistant message

Requirements:
  - ChatGPT Desktop App must be running
  - Terminal/IDE must have Accessibility permissions
"""

import sys
import time
import argparse
import re
from typing import Optional, List

from ApplicationServices import (
    AXUIElementCreateApplication,
    AXUIElementCopyAttributeValue,
    AXUIElementPerformAction,
    kAXRoleAttribute,
    kAXValueAttribute,
    kAXDescriptionAttribute,
    kAXChildrenAttribute,
    kAXPositionAttribute,
    kAXSizeAttribute,
    kAXPressAction,
)
from AppKit import NSWorkspace, NSPasteboard
from Quartz.CoreGraphics import (
    CGEventCreateKeyboardEvent,
    CGEventCreateMouseEvent,
    CGEventCreateScrollWheelEvent,
    CGEventPost,
    CGEventSetFlags,
    CGEventSetLocation,
    CGEventSourceCreate,
    kCGEventSourceStateHIDSystemState,
    kCGHIDEventTap,
    kCGEventFlagMaskCommand,
    kCGEventLeftMouseDown,
    kCGEventLeftMouseUp,
    kCGEventMouseMoved,
    kCGMouseButtonLeft,
    kCGScrollEventUnitLine,
)


def ax_attr(element, attr_name: str):
    """Get an AX attribute value, returning None on error."""
    err_code, value = AXUIElementCopyAttributeValue(element, attr_name, None)
    if err_code == 0:
        return value
    return None


def is_chatgpt_thinking(element) -> bool:
    """
    Check if ChatGPT is thinking by looking for Stop button.

    When ChatGPT is generating a response, the Send button is replaced
    with a Stop button (labeled "Stop" or "Stop generating").
    So if we find a Stop button, ChatGPT is thinking.
    """
    buttons = []
    collect_all_buttons(element, buttons)

    for btn, desc in buttons:
        if desc and 'Stop' in desc:
            print(f"[DEBUG] ChatGPT is thinking (Stop button found: '{desc}')", file=sys.stderr)
            return True

    return False


def find_chatgpt_app():
    """Find the ChatGPT desktop app and return AX element and NSRunningApplication."""
    workspace = NSWorkspace.sharedWorkspace()
    running_apps = workspace.runningApplications()

    for app in running_apps:
        bundle_id = app.bundleIdentifier()
        name = app.localizedName()

        if (bundle_id and "chatgpt" in bundle_id.lower()) or (name and "chatgpt" in name.lower()):
            ax_app = AXUIElementCreateApplication(app.processIdentifier())
            return ax_app, app

    return None, None


def find_text_input(element, depth=0, max_depth=15) -> Optional[object]:
    """Recursively find the text input field (textarea)."""
    if depth > max_depth:
        return None

    role = ax_attr(element, kAXRoleAttribute)

    if role == "AXTextArea":
        return element

    children = ax_attr(element, kAXChildrenAttribute)
    if children:
        for child in children:
            result = find_text_input(child, depth + 1, max_depth)
            if result:
                return result

    return None


def collect_all_buttons(element, buttons: List, depth=0, max_depth=20):
    """Recursively collect all buttons with their labels.

    Checks multiple attributes since different apps use different attributes for labels:
    - AXDescription (most common)
    - kAXTitleAttribute (some apps)
    - kAXValueAttribute (fallback)
    """
    if depth > max_depth:
        return

    role = ax_attr(element, kAXRoleAttribute)

    if role == "AXButton":
        # Try multiple attributes to find the button label
        desc = ax_attr(element, kAXDescriptionAttribute)
        if not desc:
            desc = ax_attr(element, "AXTitle")
        if not desc:
            desc = ax_attr(element, kAXValueAttribute)
        buttons.append((element, desc))

    children = ax_attr(element, kAXChildrenAttribute)
    if children:
        for child in children:
            collect_all_buttons(child, buttons, depth + 1, max_depth)


def collect_assistant_messages(element, messages: List[str], depth=0, max_depth=20):
    """Recursively collect all assistant message text."""
    if depth > max_depth:
        return

    role = ax_attr(element, kAXRoleAttribute)

    # Check if this is a text element
    if role in ["AXStaticText", "AXTextArea", "AXTextField"]:
        desc = ax_attr(element, kAXDescriptionAttribute)
        value = ax_attr(element, kAXValueAttribute)

        # Prefer description, fallback to value
        text_content = desc or value
        if text_content and isinstance(text_content, str) and text_content.strip():
            messages.append(text_content.strip())

    # Recurse through children
    children = ax_attr(element, kAXChildrenAttribute)
    if children:
        for child in children:
            collect_assistant_messages(child, messages, depth + 1, max_depth)


def collect_messages_with_position(element, messages: List[tuple], depth=0, max_depth=20):
    """Recursively collect messages with their X position to distinguish user vs assistant.

    Returns list of (text, x_position) tuples.
    User messages are typically right-aligned, assistant messages left-aligned.
    """
    if depth > max_depth:
        return

    role = ax_attr(element, kAXRoleAttribute)

    # Check if this is a text element
    if role in ["AXStaticText", "AXTextArea", "AXTextField"]:
        desc = ax_attr(element, kAXDescriptionAttribute)
        value = ax_attr(element, kAXValueAttribute)

        text_content = desc or value
        if text_content and isinstance(text_content, str) and text_content.strip():
            # Get position
            position = ax_attr(element, kAXPositionAttribute)
            x_pos = 0
            if position:
                pos_str = str(position)
                pos_match = re.search(r'x:([\d.]+)', pos_str)
                if pos_match:
                    x_pos = float(pos_match.group(1))

            messages.append((text_content.strip(), x_pos))

    # Recurse through children
    children = ax_attr(element, kAXChildrenAttribute)
    if children:
        for child in children:
            collect_messages_with_position(child, messages, depth + 1, max_depth)


def set_clipboard(text: str):
    """Set clipboard content."""
    pb = NSPasteboard.generalPasteboard()
    pb.clearContents()
    pb.setString_forType_(text, "public.utf8-plain-text")


def press_cmd_a():
    """Press Cmd+A to select all."""
    event_down = CGEventCreateKeyboardEvent(None, 0x00, True)  # A key
    event_up = CGEventCreateKeyboardEvent(None, 0x00, False)

    CGEventSetFlags(event_down, kCGEventFlagMaskCommand)
    CGEventSetFlags(event_up, kCGEventFlagMaskCommand)

    CGEventPost(kCGHIDEventTap, event_down)
    time.sleep(0.05)
    CGEventPost(kCGHIDEventTap, event_up)


def press_cmd_v():
    """Press Cmd+V to paste."""
    event_down = CGEventCreateKeyboardEvent(None, 0x09, True)  # V key
    event_up = CGEventCreateKeyboardEvent(None, 0x09, False)

    CGEventSetFlags(event_down, kCGEventFlagMaskCommand)
    CGEventSetFlags(event_up, kCGEventFlagMaskCommand)

    CGEventPost(kCGHIDEventTap, event_down)
    time.sleep(0.05)
    CGEventPost(kCGHIDEventTap, event_up)


def click_at_position(x: float, y: float):
    """Click at a specific screen position."""
    mouse_down = CGEventCreateMouseEvent(None, kCGEventLeftMouseDown, (x, y), kCGMouseButtonLeft)
    mouse_up = CGEventCreateMouseEvent(None, kCGEventLeftMouseUp, (x, y), kCGMouseButtonLeft)

    CGEventPost(kCGHIDEventTap, mouse_down)
    time.sleep(0.05)
    CGEventPost(kCGHIDEventTap, mouse_up)


def get_chatgpt_message_area_coords(ax_app):
    """Get coordinates for the message area (right 2/3 of window, middle height).

    Returns (x, y) tuple or None if window not found.
    """
    windows = ax_attr(ax_app, "AXWindows")
    if not windows or len(windows) == 0:
        return None

    window = windows[0]
    position = ax_attr(window, kAXPositionAttribute)
    size = ax_attr(window, kAXSizeAttribute)

    if not position or not size:
        return None

    pos_str = str(position)
    size_str = str(size)
    pos_match = re.search(r'x:([\d.]+)\s+y:([\d.]+)', pos_str)
    size_match = re.search(r'w:([\d.]+)\s+h:([\d.]+)', size_str)

    if not pos_match or not size_match:
        return None

    win_x = float(pos_match.group(1))
    win_y = float(pos_match.group(2))
    win_width = float(size_match.group(1))
    win_height = float(size_match.group(2))

    # Message area is right 2/3 of window, middle height
    x = win_x + win_width * 0.7
    y = win_y + win_height * 0.5

    return (x, y)


def do_scroll_events(scroll_x: float, scroll_y: float, direction: str, count: int):
    """Send scroll wheel events. direction: "up" or "down"."""
    scroll_lines = 50 if direction == "up" else -50
    for _ in range(count):
        scroll_event = CGEventCreateScrollWheelEvent(None, kCGScrollEventUnitLine, 1, scroll_lines)
        CGEventSetLocation(scroll_event, (scroll_x, scroll_y))
        CGEventPost(kCGHIDEventTap, scroll_event)
        time.sleep(0.1)


def get_visible_message_snapshot(ax_app) -> set:
    """Get a snapshot of currently visible message text (first 100 chars of each)."""
    messages = []
    collect_assistant_messages(ax_app, messages)
    # Use first 100 chars as key
    return set(msg[:100] for msg in messages if len(msg) > 20)


def scroll_to_bottom(ax_app, ns_app, debug: bool = False) -> bool:
    """Scroll to the very bottom of ChatGPT conversation.

    Strategy: Keep scrolling down until the visible messages stop changing.

    Returns True if successful.
    """
    coords = get_chatgpt_message_area_coords(ax_app)
    if not coords:
        if debug:
            print("[DEBUG] Could not get message area coordinates", file=sys.stderr)
        return False

    scroll_x, scroll_y = coords

    # Activate app and move mouse
    ns_app.activateWithOptions_(1)
    time.sleep(0.3)
    move_event = CGEventCreateMouseEvent(None, kCGEventMouseMoved, (scroll_x, scroll_y), 0)
    CGEventPost(kCGHIDEventTap, move_event)
    time.sleep(0.2)

    if debug:
        print(f"[DEBUG] Starting scroll to bottom at ({scroll_x:.0f}, {scroll_y:.0f})", file=sys.stderr)

    # Keep scrolling down until content stops changing
    last_snapshot = get_visible_message_snapshot(ax_app)
    stable_count = 0
    max_rounds = 50  # Safety limit

    for round_num in range(max_rounds):
        # Scroll down aggressively
        do_scroll_events(scroll_x, scroll_y, "down", 5)
        time.sleep(0.3)

        # Check if content changed
        current_snapshot = get_visible_message_snapshot(ax_app)

        if current_snapshot == last_snapshot:
            stable_count += 1
            if debug:
                print(f"[DEBUG] Round {round_num+1}: stable ({stable_count}/3)", file=sys.stderr)
            if stable_count >= 3:
                # We're at the bottom
                if debug:
                    print(f"[DEBUG] Reached bottom after {round_num+1} rounds", file=sys.stderr)
                break
        else:
            stable_count = 0
            if debug:
                print(f"[DEBUG] Round {round_num+1}: content changed, continuing", file=sys.stderr)

        last_snapshot = current_snapshot

    # Hide app
    ns_app.hide()
    time.sleep(0.2)

    return True


def collect_all_visible_messages(ax_app, x_threshold: float = 650) -> List[tuple]:
    """Collect all visible messages with their role.

    Returns list of (message_text, is_user) tuples.

    KNOWN ISSUES / TODO:
    - x_threshold=650 is hardcoded based on observed ChatGPT layout. May break if
      window is resized or ChatGPT UI changes. Should dynamically calculate threshold
      based on window width.
    - Messages < 50 chars are filtered out, which could miss very short user messages.
    - Non-ASCII first char filter (ord >= 128) may incorrectly skip valid messages
      starting with unicode characters.
    """
    visible = []
    collect_messages_with_position(ax_app, visible)

    # Filter to meaningful messages
    # TODO: This keyword list may not cover all UI elements
    ui_keywords = {'search', 'new chat', 'chatgpt', 'gpt-4', 'upgrade', 'settings', 'today', 'yesterday'}
    meaningful = []
    for msg, x_pos in visible:
        if len(msg) <= 50:
            continue
        if ord(msg[0]) >= 128:
            continue
        first_word = msg.split()[0].lower() if msg.split() else ""
        if first_word in ui_keywords:
            continue
        # DESIGN CHOICE: User messages are right-aligned (higher X position)
        # This was determined empirically by running debug-positions command
        is_user = x_pos > x_threshold
        meaningful.append((msg, is_user))

    return meaningful


def collect_turns_incrementally(ax_app, ns_app, num_turns: int, output_dir: str, debug: bool = False):
    """Collect turns one pair at a time, writing each to a file immediately.

    A "turn" is one user message followed by one assistant response.

    Algorithm:
    1. Scroll to bottom (most recent messages)
    2. Find newest unseen assistant message
    3. Scroll up to find the user message that prompted it
    4. Write pair to file immediately
    5. Repeat for num_turns
    6. If we find multiple assistants in a row, mark them seen and keep scrolling
    7. If we can't find expected message, throw RuntimeError (don't lie about success)

    KNOWN ISSUES / TODO:
    - scroll_amount=1 is very slow but necessary to not miss messages. Could be
      made adaptive based on message density.
    - 30 attempts per message search is arbitrary. May timeout on very long conversations.
    - If ChatGPT conversation has unusual structure (e.g., multiple assistant responses
      to one user message), this will mark extras as seen and may produce unexpected results.
    - The "first 100 chars as key" deduplication could fail if two messages start identically.
    """
    import os

    coords = get_chatgpt_message_area_coords(ax_app)
    if not coords:
        raise RuntimeError("Could not get ChatGPT window coordinates")

    scroll_x, scroll_y = coords

    # Scroll to bottom first
    if debug:
        print("[DEBUG] Scrolling to bottom...", file=sys.stderr)
    scroll_to_bottom(ax_app, ns_app, debug=False)

    # Activate app
    ns_app.activateWithOptions_(1)
    time.sleep(0.3)
    move_event = CGEventCreateMouseEvent(None, kCGEventMouseMoved, (scroll_x, scroll_y), 0)
    CGEventPost(kCGHIDEventTap, move_event)
    time.sleep(0.2)

    os.makedirs(output_dir, exist_ok=True)

    collected_turns = []
    seen_keys = set()  # Track what we've already collected (first 100 chars as key)
    scroll_amount = 1  # Small scrolls to not miss messages

    def find_new_message(expected_role: str) -> tuple:
        """Find a new unseen message. expected_role is 'user' or 'assistant'.
        Returns (msg, is_user) or (None, None).
        """
        ax_app_local, _ = find_chatgpt_app()
        all_msgs = collect_all_visible_messages(ax_app_local)

        for msg, is_user in all_msgs:
            key = msg[:100]
            if key not in seen_keys:
                return msg, is_user
        return None, None

    turn_num = 0
    while turn_num < num_turns:
        if debug:
            print(f"[DEBUG] Collecting turn {turn_num + 1}/{num_turns}...", file=sys.stderr)

        assistant_msg = None
        user_msg = None
        retry_count = 0
        max_retries = 3

        # Step 1: Find assistant message
        last_seen_count = len(seen_keys)
        no_new_messages_count = 0
        for attempt in range(30):
            msg, is_user = find_new_message('assistant')

            if msg:
                key = msg[:100]
                if not is_user:
                    # Found assistant
                    assistant_msg = msg
                    seen_keys.add(key)
                    if debug:
                        print(f"[DEBUG]   Found assistant ({len(msg)} chars)", file=sys.stderr)
                    break
                else:
                    # Found user when expecting assistant - we scrolled too far
                    # This user belongs to an OLDER turn, skip it
                    seen_keys.add(key)
                    if debug:
                        print(f"[DEBUG]   Skipping user message (looking for assistant)", file=sys.stderr)

            # Check if we're at the top (no new messages after scrolling)
            if len(seen_keys) == last_seen_count:
                no_new_messages_count += 1
                if no_new_messages_count >= 5:
                    # We've scrolled 5 times with no new messages - we're at the top
                    if debug:
                        print(f"[DEBUG] Reached top of conversation after {turn_num} turns", file=sys.stderr)
                    return collected_turns
            else:
                no_new_messages_count = 0
                last_seen_count = len(seen_keys)

            # Scroll up to find more
            do_scroll_events(scroll_x, scroll_y, "up", scroll_amount)
            time.sleep(0.3)

        if not assistant_msg:
            # One more check - if we found no new messages, we're at the top
            if no_new_messages_count >= 3:
                if debug:
                    print(f"[DEBUG] Reached top of conversation after {turn_num} turns", file=sys.stderr)
                return collected_turns
            raise RuntimeError(f"Could not find assistant message for turn {turn_num + 1}")

        # Step 2: Find user message (scroll up from assistant)
        last_seen_count_user = len(seen_keys)
        no_new_messages_count_user = 0
        for attempt in range(30):
            # Scroll up first
            do_scroll_events(scroll_x, scroll_y, "up", scroll_amount)
            time.sleep(0.3)

            msg, is_user = find_new_message('user')

            if msg:
                key = msg[:100]
                if is_user:
                    # Found user
                    user_msg = msg
                    seen_keys.add(key)
                    if debug:
                        print(f"[DEBUG]   Found user ({len(msg)} chars)", file=sys.stderr)
                    break
                else:
                    # Found another assistant - this shouldn't happen in normal conversation
                    # Mark as seen and keep scrolling
                    seen_keys.add(key)
                    retry_count += 1
                    if debug:
                        print(f"[DEBUG]   Found another assistant, marking seen and continuing (retry {retry_count})", file=sys.stderr)
                    if retry_count > max_retries:
                        raise RuntimeError(f"Found {retry_count} assistant messages in a row without user. Conversation may have unusual structure.")

            # Check if we're at the top (no new messages after scrolling)
            if len(seen_keys) == last_seen_count_user:
                no_new_messages_count_user += 1
                if no_new_messages_count_user >= 5:
                    # We're at the top - this assistant message has no user (first message in convo)
                    # This is unusual but possible - return what we have
                    if debug:
                        print(f"[DEBUG] Reached top of conversation (orphan assistant at start)", file=sys.stderr)
                    return collected_turns
            else:
                no_new_messages_count_user = 0
                last_seen_count_user = len(seen_keys)

        if not user_msg:
            # Check if we're at top
            if no_new_messages_count_user >= 3:
                if debug:
                    print(f"[DEBUG] Reached top of conversation after {turn_num} turns", file=sys.stderr)
                return collected_turns
            raise RuntimeError(f"Could not find user message for turn {turn_num + 1}. Found assistant but no preceding user message.")

        # Write the pair to file
        turn_num += 1
        filename = os.path.join(output_dir, f"turn{turn_num}.txt")
        with open(filename, 'w') as f:
            f.write("[USER]\n\n")
            f.write(user_msg)
            f.write("\n\n[ASSISTANT]\n\n")
            f.write(assistant_msg)
        print(f"Wrote {filename}", file=sys.stderr)

        collected_turns.append({"user": user_msg, "assistant": assistant_msg})

    # Scroll back to bottom
    if debug:
        print("[DEBUG] Scrolling back to bottom...", file=sys.stderr)
    do_scroll_events(scroll_x, scroll_y, "down", 50)
    time.sleep(0.3)

    # Hide app
    ns_app.hide()

    return collected_turns


def scroll_chatgpt(ax_app, ns_app, direction: str, amount: int = 5, debug: bool = False):
    """Scroll in ChatGPT message area.

    Args:
        ax_app: AX application element
        ns_app: NSRunningApplication
        direction: "up" or "down"
        amount: number of scroll events (each ~50 lines)
        debug: print debug info

    Returns True if scroll was performed, False on error.
    """
    coords = get_chatgpt_message_area_coords(ax_app)
    if not coords:
        if debug:
            print("[DEBUG] Could not get message area coordinates", file=sys.stderr)
        return False

    scroll_x, scroll_y = coords

    # Activate app
    ns_app.activateWithOptions_(1)
    time.sleep(0.3)

    # Move mouse to message area (no click)
    move_event = CGEventCreateMouseEvent(None, kCGEventMouseMoved, (scroll_x, scroll_y), 0)
    CGEventPost(kCGHIDEventTap, move_event)
    time.sleep(0.2)

    if debug:
        print(f"[DEBUG] Scrolling {direction} at ({scroll_x:.0f}, {scroll_y:.0f}), {amount} events", file=sys.stderr)

    do_scroll_events(scroll_x, scroll_y, direction, amount)

    time.sleep(0.3)

    # Hide app
    ns_app.hide()
    time.sleep(0.2)

    return True


def send_prompt(prompt: str, wait_for_reply: bool = True, wait_seconds: int = 180) -> str:
    """
    Send a prompt to ChatGPT Desktop App and optionally wait for response.

    Args:
        prompt: The text to send
        wait_for_reply: Whether to wait for and return the response
        wait_seconds: Maximum seconds to wait for response (default: 180s for complex queries with web search)

    Returns:
        The response text if wait_for_reply is True, empty string otherwise
    """
    ax_app, ns_app = find_chatgpt_app()
    if not ax_app:
        print("ERROR: ChatGPT app not found. Is it running?", file=sys.stderr)
        sys.exit(1)

    text_input = find_text_input(ax_app)
    if not text_input:
        print("ERROR: Could not find text input field", file=sys.stderr)
        sys.exit(1)

    # CRITICAL: Wait for ChatGPT to finish thinking before proceeding
    print("[DEBUG] Checking if ChatGPT is thinking...", file=sys.stderr)
    max_wait_for_thinking = 300  # 5 minutes max
    thinking_check_count = 0
    while is_chatgpt_thinking(ax_app):
        if thinking_check_count == 0:
            print("[DEBUG] ChatGPT is thinking - waiting for it to finish...", file=sys.stderr)
        thinking_check_count += 1
        time.sleep(2)
        if thinking_check_count * 2 >= max_wait_for_thinking:
            print("ERROR: ChatGPT still thinking after 5 minutes - aborting", file=sys.stderr)
            sys.exit(1)
        # Progress update every 30 seconds
        if thinking_check_count % 15 == 0:
            print(f"[DEBUG] Still waiting for thinking to complete ({thinking_check_count * 2}s elapsed)...", file=sys.stderr)

    if thinking_check_count > 0:
        print(f"[DEBUG] Thinking complete after {thinking_check_count * 2}s", file=sys.stderr)
    else:
        print("[DEBUG] ChatGPT is ready (not thinking)", file=sys.stderr)

    # Clear any existing text in input field
    existing_input = ax_attr(text_input, kAXValueAttribute)
    if existing_input and len(existing_input.strip()) > 0:
        print(f"[DEBUG] Clearing existing text: {existing_input[:50]}...", file=sys.stderr)
        # Activate app and click into text area first
        ns_app.activateWithOptions_(1)
        time.sleep(0.3)

        # Click into text area
        position = ax_attr(text_input, kAXPositionAttribute)
        size = ax_attr(text_input, kAXSizeAttribute)
        if position and size:
            pos_str = str(position)
            size_str = str(size)
            pos_match = re.search(r'x:([\d.]+)\s+y:([\d.]+)', pos_str)
            size_match = re.search(r'w:([\d.]+)\s+h:([\d.]+)', size_str)
            if pos_match and size_match:
                click_x = float(pos_match.group(1)) + float(size_match.group(1)) / 2
                click_y = float(pos_match.group(2)) + float(size_match.group(2)) / 2
                click_at_position(click_x, click_y)
                time.sleep(0.3)

        # Select all (Cmd+A) and delete
        source = CGEventSourceCreate(kCGEventSourceStateHIDSystemState)
        # Cmd+A to select all
        cmd_a_down = CGEventCreateKeyboardEvent(source, 0, True)  # 'a' key
        CGEventSetFlags(cmd_a_down, kCGEventFlagMaskCommand)
        cmd_a_up = CGEventCreateKeyboardEvent(source, 0, False)
        CGEventSetFlags(cmd_a_up, kCGEventFlagMaskCommand)
        CGEventPost(kCGHIDEventTap, cmd_a_down)
        CGEventPost(kCGHIDEventTap, cmd_a_up)
        time.sleep(0.2)

        # Delete key to clear selection
        delete_down = CGEventCreateKeyboardEvent(source, 51, True)  # delete key
        delete_up = CGEventCreateKeyboardEvent(source, 51, False)
        CGEventPost(kCGHIDEventTap, delete_down)
        CGEventPost(kCGHIDEventTap, delete_up)
        time.sleep(0.3)
        print("[DEBUG] Cleared existing text", file=sys.stderr)
    else:
        print("[DEBUG] Input field is clear", file=sys.stderr)

    # Set clipboard and activate app
    set_clipboard(prompt)

    ns_app.activateWithOptions_(1)  # NSApplicationActivateIgnoringOtherApps
    time.sleep(0.5)

    # Click into text area using mouse events (more reliable than kAXPressAction)
    position = ax_attr(text_input, kAXPositionAttribute)
    size = ax_attr(text_input, kAXSizeAttribute)

    if position and size:
        pos_str = str(position)
        size_str = str(size)
        pos_match = re.search(r'x:([\d.]+)\s+y:([\d.]+)', pos_str)
        size_match = re.search(r'w:([\d.]+)\s+h:([\d.]+)', size_str)

        if pos_match and size_match:
            pos_x = float(pos_match.group(1))
            pos_y = float(pos_match.group(2))
            width = float(size_match.group(1))
            height = float(size_match.group(2))

            # Click in the center of the text input
            click_x = pos_x + width / 2
            click_y = pos_y + height / 2
            click_at_position(click_x, click_y)
            time.sleep(0.5)
        else:
            # Fallback to AX action
            AXUIElementPerformAction(text_input, kAXPressAction)
            time.sleep(0.5)
    else:
        # Fallback to AX action
        AXUIElementPerformAction(text_input, kAXPressAction)
        time.sleep(0.5)

    # Select all and paste
    press_cmd_a()
    time.sleep(0.2)
    press_cmd_v()
    time.sleep(0.3)

    # Capture existing messages BEFORE sending (to filter them out later)
    existing_messages = []
    collect_assistant_messages(ax_app, existing_messages)
    existing_texts = set(existing_messages)

    # Find and click Send button
    buttons = []
    collect_all_buttons(ax_app, buttons)

    send_button = None
    for btn, desc in buttons:
        if desc and 'Send' in desc:
            send_button = btn
            print(f"[DEBUG] Found Send button: '{desc}'", file=sys.stderr)
            break

    if not send_button:
        print("ERROR: Could not find Send button", file=sys.stderr)
        print("[DEBUG] Check if ChatGPT response already exists with 'read' command", file=sys.stderr)
        sys.exit(1)

    # Get button position and click it
    position = ax_attr(send_button, kAXPositionAttribute)
    size = ax_attr(send_button, kAXSizeAttribute)

    if not position or not size:
        print("ERROR: Could not get Send button position/size", file=sys.stderr)
        sys.exit(1)

    pos_str = str(position)
    size_str = str(size)

    pos_match = re.search(r'x:([\d.]+)\s+y:([\d.]+)', pos_str)
    size_match = re.search(r'w:([\d.]+)\s+h:([\d.]+)', size_str)

    if not pos_match or not size_match:
        print("ERROR: Could not parse button position", file=sys.stderr)
        print(f"[DEBUG] position={pos_str}, size={size_str}", file=sys.stderr)
        sys.exit(1)

    pos_x = float(pos_match.group(1))
    pos_y = float(pos_match.group(2))
    width = float(size_match.group(1))
    height = float(size_match.group(2))

    # Click in the center of the button
    x = pos_x + width / 2
    y = pos_y + height / 2
    click_at_position(x, y)
    time.sleep(1.0)
    print("[DEBUG] Clicked Send button", file=sys.stderr)

    # Verify message was sent by checking if input field is now empty
    time.sleep(0.5)
    current_value = ax_attr(text_input, kAXValueAttribute)
    if current_value and len(current_value.strip()) > 0:
        print("ERROR: Message was not sent - input field still contains text", file=sys.stderr)
        print(f"[DEBUG] Input field value: {current_value[:100]}...", file=sys.stderr)
        sys.exit(1)
    print("[DEBUG] Message sent successfully (input field cleared)", file=sys.stderr)

    # Move app to background
    ns_app.hide()
    time.sleep(0.5)

    if not wait_for_reply:
        return ""

    # Poll for response
    print(f"[DEBUG] Waiting for response (timeout: {wait_seconds}s)...", file=sys.stderr)
    time.sleep(3)  # Initial wait for response to start

    last_text = ""
    last_length = 0
    stable_count = 0
    max_polls = wait_seconds * 2  # Poll every 0.5s
    poll_count = 0
    last_progress_report = 0

    for poll_count in range(max_polls):
        messages = []
        collect_assistant_messages(ax_app, messages)

        if messages:
            # Filter out existing messages and user's query
            new_messages = [
                msg for msg in messages
                if msg not in existing_texts
                and len(msg) > 1
                and ord(msg[0]) < 128
                and prompt not in msg
            ]

            if new_messages:
                current_text = max(new_messages, key=len)
            else:
                current_text = ""

            current_length = len(current_text)

            # Progress reporting every 10 seconds if text is growing
            elapsed = poll_count * 0.5
            if current_length > last_length and elapsed - last_progress_report >= 10:
                print(f"[DEBUG] Response streaming... ({current_length} chars, {elapsed:.0f}s elapsed)", file=sys.stderr)
                last_progress_report = elapsed

            # Only consider non-empty responses as stable
            if current_text and current_text == last_text:
                stable_count += 1
                if stable_count >= 4:  # Stable for 2 seconds
                    print(f"[DEBUG] Response complete ({current_length} chars)", file=sys.stderr)
                    return current_text
            else:
                last_text = current_text
                last_length = current_length
                stable_count = 0

        time.sleep(0.5)

    # Timeout - check if response was still growing
    if last_length > 0:
        if stable_count > 0:  # Text was changing near timeout (not yet stable)
            print(f"[WARNING] Timeout reached but response still streaming ({last_length} chars)", file=sys.stderr)
            print(f"[WARNING] Returning partial response. Consider increasing --wait-seconds", file=sys.stderr)
        else:
            print(f"[DEBUG] Timeout reached, returning response ({last_length} chars)", file=sys.stderr)
    else:
        print("[WARNING] No response received - ChatGPT may be rate-limiting or query failed", file=sys.stderr)

    return last_text


def read_last_reply(show_all: bool = False, latest: bool = False, debug: bool = False, limit: int = None, output_dir: str = None) -> str:
    """Read the last assistant message from ChatGPT Desktop App.

    Args:
        show_all: If True, return all messages separated by newlines
        latest: If True, return the most recent message (default: longest message)
        debug: If True, print debug info about messages found
        limit: If specified with show_all, use scrolling to collect last N turns
        output_dir: If specified, write each turn to a separate file in this directory

    Returns:
        The assistant's response text
    """
    import os

    ax_app, ns_app = find_chatgpt_app()
    if not ax_app:
        print("ERROR: ChatGPT app not found. Is it running?", file=sys.stderr)
        sys.exit(1)

    # If --all --limit N is specified, use scrolling to collect turns
    if show_all and limit and limit > 0:
        if debug:
            print(f"[DEBUG] Collecting {limit} turns", file=sys.stderr)

        # If output_dir specified, use incremental collection (one pair at a time)
        if output_dir:
            # Let RuntimeError propagate up to cmd_read_all for proper handling
            collected = collect_turns_incrementally(ax_app, ns_app, limit, output_dir, debug=debug)
            return f"Wrote {len(collected)} turns to {output_dir}"

        # Non-output-dir mode: not supported with new incremental approach
        print("ERROR: --limit requires --output-dir", file=sys.stderr)
        sys.exit(1)

        # Format output
        result = []
        total = len(turns)
        for i, (msg, is_user) in enumerate(turns, 1):
            role = "USER" if is_user else "ASSISTANT"
            label = "LATEST" if i == total else ""
            result.append(f"=== TURN {i}/{total} [{role}] {label} ({len(msg)} chars) ===\n\n{msg}")
        return "\n\n" + "="*60 + "\n\n".join(result)

    # Original behavior for non-scrolling cases
    messages = []
    collect_assistant_messages(ax_app, messages)

    if not messages:
        if debug:
            print("[DEBUG] No messages found", file=sys.stderr)
        return ""

    # Filter to meaningful messages (ASCII text, more than 1 char)
    meaningful_messages = [msg for msg in messages if len(msg) > 1 and ord(msg[0]) < 128]

    # Remove duplicates while preserving order
    seen = set()
    unique_messages = []
    for msg in meaningful_messages:
        # Use first 100 chars as key to detect duplicates
        key = msg[:100]
        if key not in seen:
            seen.add(key)
            unique_messages.append(msg)

    meaningful_messages = unique_messages

    if debug:
        print(f"[DEBUG] Found {len(messages)} total messages, {len(meaningful_messages)} meaningful unique", file=sys.stderr)
        for i, msg in enumerate(meaningful_messages):
            preview = msg[:80].replace('\n', ' ')
            print(f"[DEBUG] Message {i+1}: {len(msg)} chars - {preview}...", file=sys.stderr)

    if not meaningful_messages:
        if debug:
            print("[DEBUG] No meaningful messages, returning last raw message", file=sys.stderr)
        return messages[-1]

    if show_all:
        # Sort messages by length to get them in rough chronological order
        # (earlier messages tend to be shorter, later ones longer)
        # But reverse so newest is last
        sorted_messages = sorted(meaningful_messages, key=len)

        # Return all messages, separated by horizontal rules and numbered
        result = []
        for i, msg in enumerate(sorted_messages, 1):
            result.append(f"=== MESSAGE {i}/{len(sorted_messages)} ({len(msg)} chars) ===\n\n{msg}")
        return "\n\n" + "="*60 + "\n\n".join(result)

    if latest:
        # Return the last (most recent) message
        if debug and len(meaningful_messages) > 1:
            print(f"[DEBUG] Multiple messages found, returning latest ({len(meaningful_messages[-1])} chars)", file=sys.stderr)
        return meaningful_messages[-1]

    # Return longest message (most likely the main response)
    longest = max(meaningful_messages, key=len)

    if debug and len(meaningful_messages) > 1:
        print(f"[DEBUG] Multiple messages found, returning longest ({len(longest)} chars)", file=sys.stderr)

    return longest


# --------------- CLI layer --------------- #

def cmd_send(args):
    prompt = args.prompt
    if not prompt:
        prompt = sys.stdin.read()

    text = send_prompt(prompt, wait_for_reply=not args.no_wait, wait_seconds=args.wait_seconds)

    if not args.no_wait and text:
        sys.stdout.write(text)
        if not text.endswith("\n"):
            sys.stdout.write("\n")


def cmd_read_latest(args):
    """Read the most recent assistant message."""
    text = read_last_reply(show_all=False, latest=True, debug=args.debug, limit=None, output_dir=None)
    sys.stdout.write(text)
    if not text.endswith("\n"):
        sys.stdout.write("\n")


def cmd_read_all(args):
    """Read the entire conversation by scrolling.

    CRITICAL: This command fails completely if collection is incomplete.
    No partial output is produced - either we get everything or nothing.
    This prevents hiding errors and proceeding with incomplete data.
    """
    import os
    import shutil

    # Default to 100 turns if not specified
    limit = args.limit if args.limit else 100
    output_dir = args.output_dir if args.output_dir else "/tmp/chatgpt_conversation"

    # Clean output dir first to avoid mixing with old data
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir, exist_ok=True)

    # Attempt collection - RuntimeError is raised on failure
    # Clean up partial files on any failure - no partial output ever
    try:
        text = read_last_reply(show_all=True, latest=False, debug=args.debug, limit=limit, output_dir=output_dir)
    except RuntimeError as e:
        # Clean up partial files on failure
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)
        print(f"\n{'='*60}", file=sys.stderr)
        print("FATAL ERROR - COLLECTION FAILED", file=sys.stderr)
        print('='*60, file=sys.stderr)
        print(f"REASON: {e}", file=sys.stderr)
        print(f"{'='*60}", file=sys.stderr)
        print("NO DATA OUTPUT - partial files deleted", file=sys.stderr)
        print("You MUST fix the issue and re-run to get complete data.", file=sys.stderr)
        print(f"{'='*60}\n", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        # Catch any other unexpected errors
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)
        print(f"\n{'='*60}", file=sys.stderr)
        print("FATAL ERROR - UNEXPECTED FAILURE", file=sys.stderr)
        print('='*60, file=sys.stderr)
        print(f"TYPE: {type(e).__name__}", file=sys.stderr)
        print(f"REASON: {e}", file=sys.stderr)
        print(f"{'='*60}", file=sys.stderr)
        print("NO DATA OUTPUT - partial files deleted", file=sys.stderr)
        print(f"{'='*60}\n", file=sys.stderr)
        sys.exit(1)

    print(text, file=sys.stderr)

    # Output all collected files to stdout
    files = sorted([f for f in os.listdir(output_dir) if f.startswith("turn") and f.endswith(".txt")])

    if not files:
        print("FATAL: No turns collected. Conversation may be empty or script failed.", file=sys.stderr)
        sys.exit(1)

    print(f"\n{'='*60}", file=sys.stderr)
    print(f"SUCCESS: Collected {len(files)} turns to {output_dir}", file=sys.stderr)
    print(f"{'='*60}\n", file=sys.stderr)

    for f in files:
        filepath = os.path.join(output_dir, f)
        with open(filepath, 'r') as fp:
            content = fp.read()
            print(f"\n{'='*60}")
            print(f"=== {f} ===")
            print('='*60)
            print(content)


def cmd_test(args):
    """Test if ChatGPT app can be found and basic connectivity works."""
    print("Testing ChatGPT Desktop automation...", file=sys.stderr)

    ax_app, ns_app = find_chatgpt_app()
    if not ax_app:
        print("✗ FAIL: ChatGPT app not found. Is it running?", file=sys.stderr)
        sys.exit(1)

    print("✓ ChatGPT app found", file=sys.stderr)

    # Try to find text input
    text_input = find_text_input(ax_app)
    if not text_input:
        print("✗ FAIL: Could not find text input field", file=sys.stderr)
        sys.exit(1)

    print("✓ Text input field found", file=sys.stderr)

    # Try to collect buttons
    buttons = []
    collect_all_buttons(ax_app, buttons)
    send_button = None
    for btn, desc in buttons:
        if desc and 'Send' in desc:
            send_button = btn
            break

    if send_button:
        print("✓ Send button found", file=sys.stderr)
    else:
        print("⚠ Send button not found (ChatGPT may already be responding)", file=sys.stderr)
        print("  This is normal if there's already a response ready", file=sys.stderr)

    print("\n✓ TEST PASSED: ChatGPT Desktop automation is functional", file=sys.stderr)
    sys.exit(0)


def cmd_debug_positions(args):
    """Debug: show message positions to understand user vs assistant alignment."""
    ax_app, _ = find_chatgpt_app()
    if not ax_app:
        print("ERROR: ChatGPT app not found. Is it running?", file=sys.stderr)
        sys.exit(1)

    messages = []
    collect_messages_with_position(ax_app, messages)

    # Filter meaningful messages
    meaningful = [(text, x) for text, x in messages if len(text) > 50]

    print(f"Found {len(meaningful)} messages with positions:\n")
    for text, x_pos in meaningful:
        preview = text[:60].replace('\n', ' ')
        print(f"X={x_pos:6.0f}  {preview}...")


def cmd_scroll(args):
    """Test scroll functionality."""
    ax_app, ns_app = find_chatgpt_app()
    if not ax_app:
        print("ERROR: ChatGPT app not found. Is it running?", file=sys.stderr)
        sys.exit(1)

    direction = args.direction

    if direction == "bottom":
        print("Scrolling to bottom...", file=sys.stderr)
        success = scroll_to_bottom(ax_app, ns_app, debug=True)
        if success:
            print("✓ Scrolled to bottom", file=sys.stderr)
        else:
            print("✗ Scroll failed", file=sys.stderr)
            sys.exit(1)
    else:
        amount = args.amount
        print(f"Scrolling {direction} {amount} times...", file=sys.stderr)
        success = scroll_chatgpt(ax_app, ns_app, direction, amount, debug=True)

        if success:
            print(f"✓ Scroll {direction} complete", file=sys.stderr)
        else:
            print(f"✗ Scroll failed", file=sys.stderr)
            sys.exit(1)


def build_parser():
    p = argparse.ArgumentParser(
        description="Automate ChatGPT Desktop App via macOS Accessibility API."
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    p_send = sub.add_parser("send", help="Send a prompt to ChatGPT (reads from arg or stdin).")
    p_send.add_argument("prompt", nargs="?", help="Prompt text. If omitted, read from stdin.")
    p_send.add_argument(
        "--no-wait",
        action="store_true",
        help="Do not wait for a reply (fire-and-forget).",
    )
    p_send.add_argument(
        "--wait-seconds",
        type=int,
        default=180,
        help="Maximum seconds to wait for response (default: 180).",
    )
    p_send.set_defaults(func=cmd_send)

    p_read_latest = sub.add_parser("read_latest", help="Read the most recent assistant message.")
    p_read_latest.add_argument(
        "--debug",
        action="store_true",
        help="Show debug info about messages found",
    )
    p_read_latest.set_defaults(func=cmd_read_latest)

    p_read_all = sub.add_parser("read_all", help="Read the ENTIRE conversation by scrolling (outputs to stdout).")
    p_read_all.add_argument(
        "--debug",
        action="store_true",
        help="Show debug info about messages found",
    )
    p_read_all.add_argument(
        "--limit",
        type=int,
        default=100,
        help="Maximum turns to collect (default: 100)",
    )
    p_read_all.add_argument(
        "--output-dir",
        type=str,
        default="/tmp/chatgpt_conversation",
        help="Directory to write turn files (default: /tmp/chatgpt_conversation)",
    )
    p_read_all.set_defaults(func=cmd_read_all)

    p_test = sub.add_parser("test", help="Test if ChatGPT Desktop automation is working.")
    p_test.set_defaults(func=cmd_test)

    p_debug = sub.add_parser("debug-positions", help="Debug: show X positions of messages")
    p_debug.set_defaults(func=cmd_debug_positions)

    # NOTE: scroll command removed - scrolling should only happen internally as part of read_all
    # Exposing scroll as standalone command allows destructive state changes that lose data

    return p


def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
