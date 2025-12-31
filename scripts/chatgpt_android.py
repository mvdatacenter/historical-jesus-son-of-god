#!/usr/bin/env python3
"""
chatgpt_android.py

Read messages from ChatGPT Android app via ADB.

Requirements:
  - ADB installed and in PATH
  - Android device connected with USB debugging enabled
  - ChatGPT app open on the device

Usage:
  poetry run python scripts/chatgpt_android.py read_latest
"""

import subprocess
import sys
import xml.etree.ElementTree as ET
import tempfile
import os
import argparse


CHATGPT_PACKAGE = "com.openai.chatgpt"


def run_adb(args: list[str], check: bool = True) -> subprocess.CompletedProcess:
    """Run an ADB command."""
    cmd = ["adb"] + args
    return subprocess.run(cmd, capture_output=True, text=True, check=check)


def check_device_connected() -> bool:
    """Check if an Android device is connected."""
    result = run_adb(["devices"], check=False)
    lines = result.stdout.strip().split("\n")
    # First line is header, subsequent lines are devices
    devices = [line for line in lines[1:] if line.strip() and "device" in line]
    return len(devices) > 0


def check_chatgpt_foreground() -> bool:
    """Check if ChatGPT app is in foreground."""
    result = run_adb(["shell", "dumpsys", "window", "windows", "|", "grep", "-E", "mCurrentFocus"], check=False)
    return CHATGPT_PACKAGE in result.stdout


def dump_ui_hierarchy() -> str:
    """Dump UI hierarchy to XML and return content."""
    # Dump to device
    device_path = "/sdcard/window_dump.xml"
    run_adb(["shell", "uiautomator", "dump", device_path])

    # Pull to local temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
        temp_path = f.name

    try:
        run_adb(["pull", device_path, temp_path])
        with open(temp_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)
        # Clean up device file
        run_adb(["shell", "rm", device_path], check=False)


def extract_messages_from_xml(xml_content: str) -> list[dict]:
    """Extract text messages from UI hierarchy XML.

    Returns list of dicts with 'text', 'bounds', and heuristic 'is_assistant'.
    """
    messages = []

    try:
        root = ET.fromstring(xml_content)
    except ET.ParseError as e:
        print(f"ERROR: Failed to parse UI XML: {e}", file=sys.stderr)
        return []

    # Find all nodes with text content
    for node in root.iter('node'):
        text = node.get('text', '')
        if not text or len(text) < 20:
            continue

        # Skip UI elements (buttons, labels, etc.)
        class_name = node.get('class', '')
        if 'Button' in class_name or 'EditText' in class_name:
            continue

        # Skip obvious UI text
        lower_text = text.lower()
        if any(skip in lower_text for skip in ['chatgpt', 'new chat', 'upgrade', 'settings', 'search']):
            continue

        bounds = node.get('bounds', '')
        resource_id = node.get('resource-id', '')

        # Heuristic: assistant messages tend to be on the left, user on the right
        # Parse bounds [x1,y1][x2,y2]
        is_assistant = True
        if bounds:
            try:
                # bounds format: [x1,y1][x2,y2]
                parts = bounds.replace('][', ',').replace('[', '').replace(']', '').split(',')
                if len(parts) >= 2:
                    x1 = int(parts[0])
                    # If message starts far right (>60% of typical screen), likely user message
                    # This is a rough heuristic - screen widths vary
                    if x1 > 600:
                        is_assistant = False
            except (ValueError, IndexError):
                pass

        messages.append({
            'text': text,
            'bounds': bounds,
            'is_assistant': is_assistant,
            'resource_id': resource_id,
        })

    return messages


def read_latest(debug: bool = False) -> str:
    """Read the most recent message from ChatGPT Android app."""
    if not check_device_connected():
        print("ERROR: No Android device connected. Enable USB debugging and connect device.", file=sys.stderr)
        sys.exit(1)

    if debug:
        print("[DEBUG] Device connected", file=sys.stderr)

    # Dump UI
    if debug:
        print("[DEBUG] Dumping UI hierarchy...", file=sys.stderr)

    xml_content = dump_ui_hierarchy()

    if debug:
        print(f"[DEBUG] Got {len(xml_content)} bytes of XML", file=sys.stderr)

    # Extract messages
    messages = extract_messages_from_xml(xml_content)

    if debug:
        print(f"[DEBUG] Found {len(messages)} message candidates", file=sys.stderr)
        for i, msg in enumerate(messages):
            preview = msg['text'][:60].replace('\n', ' ')
            role = "ASST" if msg['is_assistant'] else "USER"
            print(f"[DEBUG] {i+1}. [{role}] {preview}...", file=sys.stderr)

    if not messages:
        print("ERROR: No messages found. Is ChatGPT app open with a conversation?", file=sys.stderr)
        return ""

    # Get assistant messages, return the last (most recent) one
    assistant_msgs = [m for m in messages if m['is_assistant']]

    if not assistant_msgs:
        # Fallback: return longest message
        longest = max(messages, key=lambda m: len(m['text']))
        return longest['text']

    # Return the last assistant message (bottom of screen = most recent)
    # Sort by Y position from bounds
    def get_y(msg):
        bounds = msg.get('bounds', '')
        try:
            parts = bounds.replace('][', ',').replace('[', '').replace(']', '').split(',')
            if len(parts) >= 2:
                return int(parts[1])  # y1
        except (ValueError, IndexError):
            pass
        return 0

    assistant_msgs.sort(key=get_y, reverse=True)
    return assistant_msgs[0]['text']


def cmd_read_latest(args):
    """CLI handler for read_latest command."""
    text = read_latest(debug=args.debug)
    if text:
        print(text)
        if not text.endswith('\n'):
            print()


def cmd_dump(args):
    """Dump raw UI XML for debugging."""
    if not check_device_connected():
        print("ERROR: No Android device connected.", file=sys.stderr)
        sys.exit(1)

    xml_content = dump_ui_hierarchy()
    print(xml_content)


def build_parser():
    p = argparse.ArgumentParser(
        description="Read messages from ChatGPT Android app via ADB."
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    p_read = sub.add_parser("read_latest", help="Read the most recent assistant message.")
    p_read.add_argument("--debug", action="store_true", help="Show debug info")
    p_read.set_defaults(func=cmd_read_latest)

    p_dump = sub.add_parser("dump", help="Dump raw UI XML for debugging.")
    p_dump.set_defaults(func=cmd_dump)

    return p


def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
