#!/usr/bin/env python3
"""
chatgpt_android.py

Read messages from ChatGPT Android app - FULLY AUTOMATED.

Uses Shizuku + rish to run uiautomator and read the ChatGPT UI directly.
No manual copying required.

Setup (one-time):
  1. Install Shizuku from Play Store/F-Droid
  2. Enable Developer Options → Wireless debugging
  3. Start Shizuku via wireless debugging
  4. In Shizuku: enable "Use Shizuku in terminal apps"
  5. Export rish files and move to Termux:
     mv ~/storage/shared/rish/rish /data/data/com.termux/files/usr/bin/
     mv ~/storage/shared/rish/rish_shizuku.dex /data/data/com.termux/files/usr/bin/
     chmod +x /data/data/com.termux/files/usr/bin/rish

Usage:
  python scripts/chatgpt_android.py read_latest
"""

import subprocess
import sys
import os

# Paths
TERMUX_BIN = "/data/data/com.termux/files/usr/bin"
RISH_CMD = os.path.join(TERMUX_BIN, "rish")
UI_DUMP_PATH = "/sdcard/chatgpt_ui_dump.xml"


def check_rish() -> bool:
    """Check if rish is available."""
    return os.path.exists(RISH_CMD) and os.access(RISH_CMD, os.X_OK)


def run_rish(command: str, debug: bool = False) -> tuple[bool, str]:
    """Run a command via rish (Shizuku elevated shell)."""
    if not check_rish():
        return False, "rish not found"

    try:
        result = subprocess.run(
            [RISH_CMD, "-c", command],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,  # Combine stderr into stdout
            text=True,
            timeout=30
        )
        if debug:
            print(f"[DEBUG] rish command: {command}", file=sys.stderr)
            print(f"[DEBUG] output: {result.stdout[:200]}", file=sys.stderr)
        return result.returncode == 0, result.stdout
    except subprocess.TimeoutExpired:
        return False, "Command timed out"
    except Exception as e:
        return False, str(e)


def dump_ui(debug: bool = False) -> str:
    """Dump ChatGPT UI hierarchy via uiautomator.

    Switches to ChatGPT app, dumps UI, switches back to Termux.
    """
    import time

    # Bring ChatGPT to foreground
    if debug:
        print("[DEBUG] Switching to ChatGPT...", file=sys.stderr)
    run_rish("am start -n com.openai.chatgpt/.MainActivity", debug)
    time.sleep(1.5)  # Wait for app to come to foreground

    # Dump UI
    success, output = run_rish(f"uiautomator dump {UI_DUMP_PATH}", debug)
    if not success:
        print(f"ERROR: uiautomator dump failed: {output}", file=sys.stderr)
        # Switch back to Termux before returning
        run_rish("am start -n com.termux/.app.TermuxActivity", debug)
        return ""

    # Read the dump file
    success, content = run_rish(f"cat {UI_DUMP_PATH}", debug)

    # Switch back to Termux
    if debug:
        print("[DEBUG] Switching back to Termux...", file=sys.stderr)
    run_rish("am start -n com.termux/.app.TermuxActivity", debug)

    if not success:
        print(f"ERROR: Failed to read UI dump: {content}", file=sys.stderr)
        return ""

    # Clean up
    run_rish(f"rm {UI_DUMP_PATH}", debug)

    return content


def extract_messages(xml_content: str, debug: bool = False) -> list[str]:
    """Extract messages from UI hierarchy XML using regex.

    Returns list of message texts (strings).
    """
    import re
    import html

    # Find all text attributes
    texts = re.findall(r'text="([^"]+)"', xml_content)

    # Filter and clean
    skip_words = ['chatgpt', 'new chat', 'upgrade', 'settings', 'search',
                  'today', 'yesterday', 'gpt-4', 'send', 'attach', 'ask chatgpt',
                  'sources', 'thought for']
    messages = []
    for t in texts:
        if len(t) < 30:
            continue
        lower = t.lower()
        if any(s in lower for s in skip_words):
            continue
        # Decode HTML entities
        t = html.unescape(t)
        messages.append(t)

    if debug:
        print(f"[DEBUG] Found {len(messages)} messages", file=sys.stderr)

    return messages


def read_latest(debug: bool = False) -> str:
    """Read the latest ChatGPT message from the app UI."""
    if not check_rish():
        print("ERROR: rish not found.", file=sys.stderr)
        print("", file=sys.stderr)
        print("Setup Shizuku + rish:", file=sys.stderr)
        print("  1. Install Shizuku from Play Store/F-Droid", file=sys.stderr)
        print("  2. Enable Developer Options → Wireless debugging", file=sys.stderr)
        print("  3. Start Shizuku via wireless debugging", file=sys.stderr)
        print("  4. In Shizuku: 'Use Shizuku in terminal apps'", file=sys.stderr)
        print("  5. Export rish files to Termux bin:", file=sys.stderr)
        print("     mv rish /data/data/com.termux/files/usr/bin/", file=sys.stderr)
        print("     chmod +x /data/data/com.termux/files/usr/bin/rish", file=sys.stderr)
        sys.exit(1)

    # Dump UI (switches to ChatGPT and back)
    if debug:
        print("[DEBUG] Dumping ChatGPT UI...", file=sys.stderr)
    xml_content = dump_ui(debug)

    if not xml_content:
        print("ERROR: Failed to dump UI. Is ChatGPT app installed?", file=sys.stderr)
        return ""

    # Extract messages
    messages = extract_messages(xml_content, debug)

    if not messages:
        print("No messages found in ChatGPT.", file=sys.stderr)
        return ""

    # Return the last (most recent) message
    return messages[-1]


def cmd_read_latest(args):
    """Read the latest ChatGPT message."""
    text = read_latest(debug=args.debug)
    if text:
        print(text)
        if not text.endswith('\n'):
            print()


def cmd_test(args):
    """Test Shizuku/rish setup."""
    print("Checking Shizuku + rish setup...", file=sys.stderr)

    if not check_rish():
        print("✗ rish not found at", RISH_CMD, file=sys.stderr)
        print("  See setup instructions in script header", file=sys.stderr)
        sys.exit(1)

    print("✓ rish found", file=sys.stderr)

    # Test rish works
    success, output = run_rish("id")
    if not success:
        print(f"✗ rish failed: {output}", file=sys.stderr)
        print("  Is Shizuku running?", file=sys.stderr)
        sys.exit(1)

    print(f"✓ rish works: {output.strip()}", file=sys.stderr)

    # Test uiautomator
    success, output = run_rish("uiautomator dump /sdcard/test_dump.xml")
    if success:
        run_rish("rm /sdcard/test_dump.xml")
        print("✓ uiautomator works", file=sys.stderr)
    else:
        print(f"✗ uiautomator failed: {output}", file=sys.stderr)
        sys.exit(1)

    print("\n✓ All checks passed! Ready to read ChatGPT.", file=sys.stderr)


def cmd_dump(args):
    """Dump raw UI XML for debugging."""
    xml = dump_ui(debug=True)
    if xml:
        print(xml)


def main():
    import argparse

    p = argparse.ArgumentParser(
        description="Read ChatGPT messages from Android app via Shizuku."
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    p_read = sub.add_parser("read_latest", help="Read latest ChatGPT message")
    p_read.add_argument("--debug", action="store_true", help="Show debug info")
    p_read.set_defaults(func=cmd_read_latest)

    p_test = sub.add_parser("test", help="Test Shizuku/rish setup")
    p_test.set_defaults(func=cmd_test)

    p_dump = sub.add_parser("dump", help="Dump raw UI XML")
    p_dump.set_defaults(func=cmd_dump)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
