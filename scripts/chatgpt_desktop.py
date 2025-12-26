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
import hashlib
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
    kAXOrientationAttribute,
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

    # First pass: look for exact bundle ID match (preferred)
    for app in running_apps:
        bundle_id = app.bundleIdentifier()
        if bundle_id == "com.openai.chat":
            ax_app = AXUIElementCreateApplication(app.processIdentifier())
            return ax_app, app

    # Second pass: look for exact name match
    for app in running_apps:
        name = app.localizedName()
        if name == "ChatGPT":
            ax_app = AXUIElementCreateApplication(app.processIdentifier())
            return ax_app, app

    # Fallback: partial match (but avoid Helper processes)
    for app in running_apps:
        bundle_id = app.bundleIdentifier() or ""
        name = app.localizedName() or ""
        if "Helper" in name:
            continue
        if "chatgpt" in bundle_id.lower() or "chatgpt" in name.lower():
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


def collect_all_text_from_element(element, texts: List[str], depth=0, max_depth=20):
    """Recursively collect ALL text from an element and its children."""
    if depth > max_depth:
        return

    role = ax_attr(element, kAXRoleAttribute)

    if role in ["AXStaticText", "AXTextArea", "AXTextField"]:
        # Try desc first, fall back to value
        desc = ax_attr(element, kAXDescriptionAttribute)
        value = ax_attr(element, kAXValueAttribute)
        text_content = desc or value

        # Filter out UI garbage like "Thought for a couple of seconds"
        if text_content and isinstance(text_content, str) and text_content.strip():
            text = text_content.strip()
            # Skip thinking indicators
            if not text.startswith("Thought for"):
                texts.append(text)

    children = ax_attr(element, kAXChildrenAttribute)
    if children:
        for child in children:
            collect_all_text_from_element(child, texts, depth + 1, max_depth)


def has_descendant_group_with_text(element, min_text_len=20, depth=0, max_depth=10):
    """Check if element has any DESCENDANT AXGroup that contains substantial text.

    This recursively checks all descendants, not just direct children.
    """
    if depth > max_depth:
        return False

    children = ax_attr(element, kAXChildrenAttribute) or []
    for child in children:
        child_role = ax_attr(child, kAXRoleAttribute)
        if child_role == "AXGroup":
            texts = []
            collect_all_text_from_element(child, texts, 0, 10)
            substantial = [t for t in texts if len(t) > min_text_len]
            if substantial:
                return True
        # Recurse into children regardless of role
        if has_descendant_group_with_text(child, min_text_len, depth + 1, max_depth):
            return True
    return False


def collect_messages_with_position(element, messages: List[tuple], depth=0, max_depth=20, seen_texts=None):
    """Recursively collect messages with their Y position and role.

    This function finds the DEEPEST AXGroup containers that hold message content.
    It skips parent AXGroups that contain child AXGroups with text, ensuring we
    collect at the message level, not at a parent container level.

    Returns list of (text, y_position, is_assistant) tuples.
    Assistant messages have AXSubrole='AXHostingView', user messages don't.
    """
    if seen_texts is None:
        seen_texts = set()
    if depth > max_depth:
        return

    role = ax_attr(element, kAXRoleAttribute)
    children = ax_attr(element, kAXChildrenAttribute) or []

    # Check if this AXGroup is a LEAF message container (no descendant groups with text)
    if role == "AXGroup" and not has_descendant_group_with_text(element):
        texts = []
        collect_all_text_from_element(element, texts, 0, 10)

        # Filter to substantial texts only (20 chars min to exclude UI snippets)
        substantial = [t for t in texts if len(t) > 20]

        if len(substantial) >= 1:
            # Join all text from this container as one message
            joined = "\n\n".join(substantial)

            # Avoid duplicates - use MD5 hash of FULL content, not just prefix
            # (Two different messages can share the same prefix, e.g., a truncated
            # response and a complete response to a follow-up question)
            key = hashlib.md5(joined.encode()).hexdigest()
            if key not in seen_texts:
                seen_texts.add(key)

                # Get position of the container
                position = ax_attr(element, kAXPositionAttribute)
                y_pos = 0
                if position:
                    pos_str = str(position)
                    pos_match = re.search(r'y:(-?[\d.]+)', pos_str)
                    if pos_match:
                        y_pos = float(pos_match.group(1))

                # Determine if this is an assistant message by checking X position
                # User messages are right-aligned (higher X ~800+), assistant messages are left-aligned (X ~500)
                # We check the X position of the first AXStaticText child
                is_assistant = True  # default
                children = ax_attr(element, kAXChildrenAttribute) or []
                for child in children:
                    child_role = ax_attr(child, kAXRoleAttribute)
                    if child_role == "AXStaticText":
                        child_pos = ax_attr(child, kAXPositionAttribute)
                        if child_pos:
                            x_match = re.search(r'x:([\d.]+)', str(child_pos))
                            if x_match:
                                x_pos = float(x_match.group(1))
                                # User messages have higher X (right side), threshold ~700
                                is_assistant = x_pos < 700
                        break

                messages.append((joined, y_pos, is_assistant))
                return  # Don't recurse into children - we already got their text

    # Recurse through children
    for child in children:
        collect_messages_with_position(child, messages, depth + 1, max_depth, seen_texts)


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


def press_key(key_code: int):
    """Press a key by its virtual key code.

    Common key codes:
    - 36: Return/Enter
    - 51: Delete/Backspace
    - 53: Escape
    """
    source = CGEventSourceCreate(kCGEventSourceStateHIDSystemState)
    key_down = CGEventCreateKeyboardEvent(source, key_code, True)
    key_up = CGEventCreateKeyboardEvent(source, key_code, False)

    CGEventPost(kCGHIDEventTap, key_down)
    time.sleep(0.05)
    CGEventPost(kCGHIDEventTap, key_up)


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


def get_scroll_position(ax_app) -> float | None:
    """Get current vertical scroll position of the CONVERSATION scrollbar.

    Returns 0.0 = top, 1.0 = bottom, None if not found.

    ChatGPT has multiple vertical scrollbars:
    - Left sidebar (projects/conversations list) - lower X position
    - Main conversation area - higher X position (rightmost)

    We identify the conversation scrollbar by finding the vertical scrollbar
    with the highest X position.
    """
    def find_all_vertical_scrollbars(element, depth=0, results=None):
        if results is None:
            results = []
        if depth > 15:
            return results
        role = ax_attr(element, kAXRoleAttribute)
        if role == "AXScrollBar":
            orientation = ax_attr(element, kAXOrientationAttribute)
            if orientation == "AXVerticalOrientation":
                value = ax_attr(element, kAXValueAttribute)
                position = ax_attr(element, kAXPositionAttribute)
                if value is not None and position is not None:
                    # Parse X position
                    pos_str = str(position)
                    pos_match = re.search(r'x:([\d.]+)', pos_str)
                    x_pos = float(pos_match.group(1)) if pos_match else 0
                    results.append((float(value), x_pos))
        children = ax_attr(element, kAXChildrenAttribute) or []
        for child in children:
            find_all_vertical_scrollbars(child, depth + 1, results)
        return results

    scrollbars = find_all_vertical_scrollbars(ax_app)
    if not scrollbars:
        return None

    # Find the scrollbar with highest X position (rightmost = conversation)
    scrollbars.sort(key=lambda x: x[1], reverse=True)
    return scrollbars[0][0]  # Return value of rightmost scrollbar


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


def scroll_to_bottom(ax_app, ns_app, debug: bool = False, hide_after: bool = True) -> bool:
    """Scroll to the very bottom of ChatGPT conversation.

    Strategy: Check scrollbar position, scroll down until it reaches 1.0 (bottom).

    Args:
        hide_after: If True, hide app after scrolling. Set False when called
                    from within a larger operation that will continue using the app.

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
    time.sleep(0.1)
    move_event = CGEventCreateMouseEvent(None, kCGEventMouseMoved, (scroll_x, scroll_y), 0)
    CGEventPost(kCGHIDEventTap, move_event)
    time.sleep(0.1)

    if debug:
        print(f"[DEBUG] Starting scroll to bottom at ({scroll_x:.0f}, {scroll_y:.0f})", file=sys.stderr)

    # Check scrollbar position and scroll until at bottom (1.0)
    max_rounds = 50  # Safety limit
    for round_num in range(max_rounds):
        pos = get_scroll_position(ax_app)
        if pos is not None and pos >= 0.98:
            if debug:
                print(f"[DEBUG] At bottom (pos={pos:.3f}) after {round_num} scrolls", file=sys.stderr)
            break
        do_scroll_events(scroll_x, scroll_y, "down", 5)
        time.sleep(0.02)

    if hide_after:
        ns_app.hide()
        time.sleep(0.1)

    return True


def is_at_scroll_top() -> bool:
    """Check if we're at the VERY top of the conversation.

    Uses the conversation scrollbar position (rightmost vertical scrollbar).
    Returns True ONLY if scroll position is essentially 0 (top).

    This function has NO side effects - it only reads the current state.

    IMPORTANT: Use a very tight threshold (0.001) to avoid false positives.
    A loose threshold (0.02) was causing early termination of scraping.
    """
    ax_app, _ = find_chatgpt_app()
    pos = get_scroll_position(ax_app)

    # Very tight threshold - only true if we're truly at the very top
    if pos is not None and pos <= 0.001:
        return True

    return False


def collect_all_visible_messages(ax_app) -> List[tuple]:
    """Collect all visible messages with their Y position and role.

    Returns list of (message_text, y_pos, is_assistant) tuples, sorted by Y position (top to bottom).

    Messages are collected at the AXGroup container level, so fragments of the same
    response are automatically joined.
    """
    visible = []
    collect_messages_with_position(ax_app, visible)

    # Filter out UI elements
    ui_keywords = {'search', 'new chat', 'chatgpt', 'gpt-4', 'upgrade', 'settings', 'today', 'yesterday'}
    filtered = []
    for msg, y_pos, is_assistant in visible:
        if len(msg) <= 20:  # Minimum length to filter UI elements
            continue
        # NOTE: Removed ord(msg[0]) >= 128 filter - it was blocking Polish/non-ASCII content
        first_word = msg.split()[0].lower() if msg.split() else ""
        if first_word in ui_keywords:
            continue
        filtered.append((msg, y_pos, is_assistant))

    # Sort by Y position (oldest to newest - more negative Y = older/higher on screen)
    # So sort ascending: most negative first, highest Y (newest) last
    filtered.sort(key=lambda x: x[1])

    return filtered


def collect_turns_incrementally(ax_app, ns_app, num_turns: int, output_dir: str, debug: bool = False):
    """Collect turns one pair at a time, writing each to a file immediately.

    A "turn" is one user message followed by one assistant response.

    CRITICAL DESIGN: All-or-nothing collection.
    - Files are written to a TEMP directory during collection
    - Only on COMPLETE success are files moved to output_dir
    - On ANY failure, temp files are deleted and output_dir stays empty
    - This prevents partial data from being accessible

    Algorithm:
    1. Scroll to bottom (most recent messages)
    2. Find newest unseen assistant message
    3. Scroll up to find the user message that prompted it
    4. Write pair to temp file
    5. Repeat for num_turns
    6. On success: move all temp files to output_dir
    7. On failure: delete temp files, raise RuntimeError

    KNOWN ISSUES / TODO:
    - scroll_amount=1 is very slow but necessary to not miss messages. Could be
      made adaptive based on message density.
    - 30 attempts per message search is arbitrary. May timeout on very long conversations.
    - If ChatGPT conversation has unusual structure (e.g., multiple assistant responses
      to one user message), this will mark extras as seen and may produce unexpected results.
    - The "first 100 chars as key" deduplication could fail if two messages start identically.
    """
    import os
    import tempfile
    import shutil

    # Create temp directory for collection - files only move to output_dir on success
    temp_dir = tempfile.mkdtemp(prefix="chatgpt_collect_")
    state = {'complete': False}  # Mutable container for closure access

    def finalize_collection():
        """Move files from temp to output on success, or delete temp on failure."""
        if state['complete']:
            # SUCCESS: Move all files from temp to output_dir
            os.makedirs(output_dir, exist_ok=True)
            for f in os.listdir(temp_dir):
                shutil.move(os.path.join(temp_dir, f), os.path.join(output_dir, f))
        # Always clean up temp dir
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

    try:
        coords = get_chatgpt_message_area_coords(ax_app)
        if not coords:
            raise RuntimeError("Could not get ChatGPT window coordinates")

        scroll_x, scroll_y = coords

        # Scroll to bottom first (don't hide - we continue immediately)
        if debug:
            print("[DEBUG] Scrolling to bottom...", file=sys.stderr)
        scroll_to_bottom(ax_app, ns_app, debug=False, hide_after=False)

        collected_turns = []
        seen_keys = set()  # Track what we've already collected (hash of full message)
        scroll_amount = 1  # Small scrolls to not miss messages

        def msg_key(msg: str) -> str:
            """Generate a unique key for a message.
            Uses hash of full content because translation prompts often share the same prefix.
            """
            import hashlib
            return hashlib.md5(msg.encode()).hexdigest()

        def find_new_assistant_message() -> str | None:
            """Find the next unseen ASSISTANT message (by Y position, bottom to top).
            Returns message text or None if no new assistant messages visible.
            """
            ax_app_local, _ = find_chatgpt_app()
            visible = []
            collect_messages_with_position(ax_app_local, visible)

            # Filter to assistant messages only, sorted bottom to top
            assistant_msgs = [(msg, y_pos) for msg, y_pos, is_asst in visible if is_asst]
            assistant_msgs.sort(key=lambda x: x[1], reverse=True)  # highest Y (bottom) first

            for msg, y_pos in assistant_msgs:
                key = msg_key(msg)
                if key not in seen_keys:
                    return msg
            return None

        def find_new_user_message() -> str | None:
            """Find the next unseen USER message (by Y position, bottom to top).
            Returns message text or None if no new user messages visible.
            """
            ax_app_local, _ = find_chatgpt_app()
            visible = []
            collect_messages_with_position(ax_app_local, visible)

            # Filter to user messages only, sorted bottom to top
            user_msgs = [(msg, y_pos) for msg, y_pos, is_asst in visible if not is_asst]
            user_msgs.sort(key=lambda x: x[1], reverse=True)  # highest Y (bottom) first

            for msg, y_pos in user_msgs:
                key = msg_key(msg)
                if key not in seen_keys:
                    return msg
            return None

        turn_num = 0
        at_top = False
        while turn_num < num_turns and not at_top:
            # Always show progress (no content info)
            print(f"Collecting turn {turn_num + 1}/{num_turns}...", file=sys.stderr)

            assistant_msg = None
            user_msg = None

            # Step 1: Find ASSISTANT message (response)
            for attempt in range(50):
                msg = find_new_assistant_message()

                if msg:
                    assistant_msg = msg
                    seen_keys.add(msg_key(msg))
                    print(f"  Found ASSISTANT ({len(msg)} chars)", file=sys.stderr)
                    break

                # Check if we're at top before scrolling
                if is_at_scroll_top():
                    at_top = True
                    break

                # Scroll up to find more
                do_scroll_events(scroll_x, scroll_y, "up", scroll_amount)
                time.sleep(0.3)
                if debug:
                    print(f"  Scrolling... ({attempt + 1})", file=sys.stderr)

            if at_top:
                print(f"Reached top of conversation", file=sys.stderr)
                break

            if not assistant_msg:
                # Can't find assistant message - stop collecting but return what we have
                print(f"Could not find ASSISTANT message for turn {turn_num + 1}, stopping collection", file=sys.stderr)
                break

            # Step 2: Find USER message (the prompt that triggered the response)
            for attempt in range(50):
                msg = find_new_user_message()

                if msg:
                    user_msg = msg
                    seen_keys.add(msg_key(msg))
                    print(f"  Found USER ({len(msg)} chars)", file=sys.stderr)
                    break

                # Check if we're at top
                if is_at_scroll_top():
                    at_top = True
                    break

                # Scroll up to find more
                do_scroll_events(scroll_x, scroll_y, "up", scroll_amount)
                time.sleep(0.3)
                if debug:
                    print(f"  Scrolling... ({attempt + 1})", file=sys.stderr)

            if at_top:
                print(f"Reached top of conversation", file=sys.stderr)
                break

            if not user_msg:
                # Can't find user message - stop collecting but return what we have
                print(f"Could not find USER message for turn {turn_num + 1}, stopping collection", file=sys.stderr)
                break

            # Write the pair to TEMP file (not final output_dir yet)
            turn_num += 1
            filename = os.path.join(temp_dir, f"turn{turn_num}.txt")
            with open(filename, 'w') as f:
                f.write("[USER]\n\n")
                f.write(user_msg)
                f.write("\n\n[ASSISTANT]\n\n")
                f.write(assistant_msg)

            collected_turns.append({"user": user_msg, "assistant": assistant_msg})

        # Scroll back to bottom using scrollbar detection, then hide
        print(f"Scrolling back to bottom...", file=sys.stderr)
        scroll_to_bottom(ax_app, ns_app, debug=False, hide_after=True)

        # Mark collection as complete - this allows finalize_collection to move files
        state['complete'] = True
        print(f"Collection complete: {turn_num} turns", file=sys.stderr)
        return collected_turns

    finally:
        finalize_collection()


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

    # Bring ChatGPT to foreground before clicking (avoid notification overlays)
    ns_app.activateWithOptions_(1)
    time.sleep(0.3)

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
        print("[DEBUG] Click didn't work, trying Enter key as fallback...", file=sys.stderr)
        # Press Enter key as fallback
        press_key(36)  # 36 = Return/Enter key
        time.sleep(1.0)

        # Check again
        current_value = ax_attr(text_input, kAXValueAttribute)
        if current_value and len(current_value.strip()) > 0:
            print("ERROR: Message was not sent - input field still contains text", file=sys.stderr)
            print(f"[DEBUG] Input field value: {current_value[:100]}...", file=sys.stderr)
            sys.exit(1)
        print("[DEBUG] Message sent via Enter key", file=sys.stderr)
    else:
        print("[DEBUG] Message sent successfully (input field cleared)", file=sys.stderr)

    # Move app to background
    ns_app.hide()
    time.sleep(0.5)

    if not wait_for_reply:
        return ""

    # Poll for response using Stop button detection
    print(f"[DEBUG] Waiting for response (timeout: {wait_seconds}s)...", file=sys.stderr)
    time.sleep(2)  # Initial wait for response to start

    max_polls = wait_seconds * 2  # Poll every 0.5s
    last_progress_report = 0

    for poll_count in range(max_polls):
        # Check if ChatGPT is still generating (Stop button visible)
        still_thinking = is_chatgpt_thinking(ax_app)
        elapsed = poll_count * 0.5

        if still_thinking:
            # Progress reporting every 10 seconds
            if elapsed - last_progress_report >= 10:
                print(f"[DEBUG] ChatGPT still generating... ({elapsed:.0f}s elapsed)", file=sys.stderr)
                last_progress_report = elapsed
            time.sleep(0.5)
            continue

        # Stop button gone - ChatGPT finished. Now collect the response.
        print(f"[DEBUG] ChatGPT finished generating ({elapsed:.0f}s)", file=sys.stderr)
        time.sleep(0.5)  # Brief pause to let UI settle

        messages = []
        collect_assistant_messages(ax_app, messages)

        if messages:
            # Filter out existing messages and user's query
            new_messages = [
                msg for msg in messages
                if msg not in existing_texts
                and len(msg) > 1
                and not msg.startswith(prompt[:50])
            ]

            if new_messages:
                response = max(new_messages, key=len)
                print(f"[DEBUG] Response complete ({len(response)} chars)", file=sys.stderr)
                return response

        # No new message found - might need to scroll or wait longer
        print("[DEBUG] No new message found, retrying...", file=sys.stderr)
        time.sleep(0.5)

    # Timeout
    print(f"\n{'='*60}", file=sys.stderr)
    print("FATAL ERROR - TIMEOUT", file=sys.stderr)
    print('='*60, file=sys.stderr)
    print(f"ChatGPT did not finish within {wait_seconds}s", file=sys.stderr)
    print(f"Increase --wait-seconds and try again", file=sys.stderr)
    print(f"{'='*60}\n", file=sys.stderr)
    sys.exit(1)


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

    # Use grouped message collection (joins fragments of same response)
    # Returns list of (msg, y_pos, is_assistant) tuples sorted by Y position (top to bottom)
    all_messages = collect_all_visible_messages(ax_app)

    if debug:
        print(f"[DEBUG] Found {len(all_messages)} messages", file=sys.stderr)
        for i, (msg, y_pos, is_asst) in enumerate(all_messages):
            role = "ASST" if is_asst else "USER"
            preview = msg[:70].replace('\n', ' ')
            print(f"[DEBUG] Message {i+1} [{role}]: {len(msg)} chars - {preview}...", file=sys.stderr)

    if not all_messages:
        if debug:
            print("[DEBUG] No messages found", file=sys.stderr)
        return ""

    if show_all:
        # Return all messages in order (top to bottom = oldest to newest)
        result = []
        for i, (msg, y_pos, is_asst) in enumerate(all_messages, 1):
            role = "ASSISTANT" if is_asst else "USER"
            result.append(f"=== MESSAGE {i}/{len(all_messages)} [{role}] ({len(msg)} chars) ===\n\n{msg}")
        return "\n\n" + "="*60 + "\n\n".join(result)

    # Filter for assistant messages only
    assistant_messages = [(msg, y_pos) for msg, y_pos, is_asst in all_messages if is_asst]

    if not assistant_messages:
        if debug:
            print("[DEBUG] No assistant messages found", file=sys.stderr)
        return ""

    if latest:
        # Return the last (most recent / bottom-most) assistant message
        latest_msg = assistant_messages[-1][0]
        if debug:
            print(f"[DEBUG] Returning latest assistant message ({len(latest_msg)} chars)", file=sys.stderr)
        return latest_msg

    # Return longest assistant message (most likely the main response)
    longest = max(assistant_messages, key=lambda x: len(x[0]))[0]

    if debug:
        print(f"[DEBUG] Returning longest assistant message ({len(longest)} chars)", file=sys.stderr)

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
    """Read conversation by scrolling.

    CRITICAL: Requires explicit --limit N or --no-limit flag.
    This prevents accidentally scraping the entire conversation when only a few turns were requested.

    CRITICAL: This command fails completely if collection is incomplete.
    No partial output is produced - either we get everything or nothing.
    This prevents hiding errors and proceeding with incomplete data.
    """
    import os
    import shutil

    # ENFORCE: Must specify either --limit N or explicit user instruction flag
    if args.limit is None and not args.no_limit:
        print("\n" + "="*60, file=sys.stderr)
        print("ERROR: You must specify --limit N", file=sys.stderr)
        print("="*60, file=sys.stderr)
        print("\nExamples:", file=sys.stderr)
        print("  extensive_scrape_history --limit 2      # Scrape last 2 turns", file=sys.stderr)
        print("  extensive_scrape_history --limit 10     # Scrape last 10 turns", file=sys.stderr)
        print("\nUnlimited scraping requires:", file=sys.stderr)
        print("  extensive_scrape_history --user-gave-me-very-explicit-instruction-to-scrape", file=sys.stderr)
        print("\nClaude: Do NOT use the unlimited flag without explicit user instruction.", file=sys.stderr)
        print("If the user already gave you content, USE THAT instead of scraping.", file=sys.stderr)
        print("="*60 + "\n", file=sys.stderr)
        sys.exit(1)

    # Set limit: explicit value, or 100 if --no-limit
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

    # DO NOT output file contents to stdout - truncation would cause partial data exposure
    # Only list the files so user can read them individually
    print(f"Files collected ({len(files)} turns):", file=sys.stderr)
    for f in files:
        filepath = os.path.join(output_dir, f)
        size = os.path.getsize(filepath)
        print(f"  {filepath} ({size} bytes)", file=sys.stderr)


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

    p_read_all = sub.add_parser("extensive_scrape_history", help="EXPENSIVE: Scrape conversation history by scrolling. REQUIRES explicit --limit N or --no-limit.")
    p_read_all.add_argument(
        "--debug",
        action="store_true",
        help="Show debug info about messages found",
    )
    p_read_all.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Maximum turns to collect (REQUIRED unless --no-limit is set)",
    )
    p_read_all.add_argument(
        "--user-gave-me-very-explicit-instruction-to-scrape",
        action="store_true",
        dest="no_limit",
        help="ONLY use this flag if the user EXPLICITLY told you to scrape. Never use on your own initiative.",
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

    # NOTE: scroll command removed - scrolling should only happen internally as part of extensive_scrape_history
    # Exposing scroll as standalone command allows destructive state changes that lose data

    return p


def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
