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
    CGEventPost,
    CGEventSetFlags,
    kCGHIDEventTap,
    kCGEventFlagMaskCommand,
    kCGEventLeftMouseDown,
    kCGEventLeftMouseUp,
    kCGMouseButtonLeft,
)


def ax_attr(element, attr_name: str):
    """Get an AX attribute value, returning None on error."""
    err_code, value = AXUIElementCopyAttributeValue(element, attr_name, None)
    if err_code == 0:
        return value
    return None


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
    """Recursively collect all buttons with their descriptions."""
    if depth > max_depth:
        return

    role = ax_attr(element, kAXRoleAttribute)

    if role == "AXButton":
        desc = ax_attr(element, kAXDescriptionAttribute)
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
        if desc and desc == 'Send':
            send_button = btn
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


def read_last_reply(show_all: bool = False, debug: bool = False) -> str:
    """Read the last assistant message from ChatGPT Desktop App.

    Args:
        show_all: If True, return all messages separated by newlines
        debug: If True, print debug info about messages found

    Returns:
        The assistant's response text
    """
    ax_app, _ = find_chatgpt_app()
    if not ax_app:
        print("ERROR: ChatGPT app not found. Is it running?", file=sys.stderr)
        sys.exit(1)

    messages = []
    collect_assistant_messages(ax_app, messages)

    if not messages:
        if debug:
            print("[DEBUG] No messages found", file=sys.stderr)
        return ""

    # Filter to meaningful messages (ASCII text, more than 1 char)
    meaningful_messages = [msg for msg in messages if len(msg) > 1 and ord(msg[0]) < 128]

    if debug:
        print(f"[DEBUG] Found {len(messages)} total messages, {len(meaningful_messages)} meaningful", file=sys.stderr)
        for i, msg in enumerate(meaningful_messages):
            preview = msg[:80].replace('\n', ' ')
            print(f"[DEBUG] Message {i+1}: {len(msg)} chars - {preview}...", file=sys.stderr)

    if not meaningful_messages:
        if debug:
            print("[DEBUG] No meaningful messages, returning last raw message", file=sys.stderr)
        return messages[-1]

    if show_all:
        # Return all messages, separated by horizontal rules
        return ("\n\n" + "="*60 + "\n\n").join(meaningful_messages)

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


def cmd_read(args):
    text = read_last_reply(show_all=args.all, debug=args.debug)
    sys.stdout.write(text)
    if not text.endswith("\n"):
        sys.stdout.write("\n")


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
        if desc and desc == 'Send':
            send_button = btn
            break

    if send_button:
        print("✓ Send button found", file=sys.stderr)
    else:
        print("⚠ Send button not found (ChatGPT may already be responding)", file=sys.stderr)
        print("  This is normal if there's already a response ready", file=sys.stderr)

    print("\n✓ TEST PASSED: ChatGPT Desktop automation is functional", file=sys.stderr)
    sys.exit(0)


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

    p_read = sub.add_parser("read", help="Read the last assistant reply from ChatGPT.")
    p_read.add_argument(
        "--all",
        action="store_true",
        help="Show all messages found, not just the longest",
    )
    p_read.add_argument(
        "--debug",
        action="store_true",
        help="Show debug info about messages found",
    )
    p_read.set_defaults(func=cmd_read)

    p_test = sub.add_parser("test", help="Test if ChatGPT Desktop automation is working.")
    p_test.set_defaults(func=cmd_test)

    return p


def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
