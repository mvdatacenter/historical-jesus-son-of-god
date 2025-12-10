#!/usr/bin/env python3
"""
Capture the AX tree structure from ChatGPT for use in integration tests.
Run this once to save a snapshot, then use that snapshot in tests.
"""

import json
import sys
from ApplicationServices import (
    AXUIElementCreateApplication,
    AXUIElementCopyAttributeValue,
    kAXRoleAttribute,
    kAXValueAttribute,
    kAXDescriptionAttribute,
    kAXChildrenAttribute,
    kAXPositionAttribute,
)
from AppKit import NSWorkspace
import re


def ax_attr(element, attr_name: str):
    err_code, value = AXUIElementCopyAttributeValue(element, attr_name, None)
    if err_code == 0:
        return value
    return None


def find_chatgpt_app():
    workspace = NSWorkspace.sharedWorkspace()
    running_apps = workspace.runningApplications()
    for app in running_apps:
        bundle_id = app.bundleIdentifier()
        name = app.localizedName()
        if (bundle_id and "chatgpt" in bundle_id.lower()) or (name and "chatgpt" in name.lower()):
            ax_app = AXUIElementCreateApplication(app.processIdentifier())
            return ax_app, app
    return None, None


def serialize_element(element, depth=0, max_depth=15):
    """Serialize an AX element to a dict for JSON storage."""
    if depth > max_depth:
        return None

    role = ax_attr(element, kAXRoleAttribute)
    if not role:
        return None

    result = {
        "role": role,
        "subrole": ax_attr(element, "AXSubrole") or None,
        "children": [],
    }

    # Get position
    pos = ax_attr(element, kAXPositionAttribute)
    if pos:
        pos_str = str(pos)
        x_match = re.search(r'x:([\d.-]+)', pos_str)
        y_match = re.search(r'y:([\d.-]+)', pos_str)
        if x_match and y_match:
            result["x"] = float(x_match.group(1))
            result["y"] = float(y_match.group(1))

    # Get text content (only for text elements)
    if role in ["AXStaticText", "AXTextArea", "AXTextField"]:
        desc = ax_attr(element, kAXDescriptionAttribute)
        value = ax_attr(element, kAXValueAttribute)
        if desc and isinstance(desc, str):
            result["desc"] = desc
        if value and isinstance(value, str):
            result["value"] = value

    # Recurse children
    children = ax_attr(element, kAXChildrenAttribute) or []
    for child in children:
        child_data = serialize_element(child, depth + 1, max_depth)
        if child_data:
            result["children"].append(child_data)

    return result


def find_conversation_area(element, depth=0):
    """Find the conversation AXList/AXSectionList."""
    if depth > 15:
        return None

    role = ax_attr(element, kAXRoleAttribute)
    subrole = ax_attr(element, "AXSubrole")

    if role == "AXList" and subrole == "AXSectionList":
        # Check if this contains messages (not sidebar)
        children = ax_attr(element, kAXChildrenAttribute) or []
        for child in children:
            gc = ax_attr(child, kAXChildrenAttribute) or []
            for g in gc:
                ggc = ax_attr(g, kAXChildrenAttribute) or []
                for gg in ggc:
                    r = ax_attr(gg, kAXRoleAttribute)
                    if r == "AXStaticText":
                        d = ax_attr(gg, kAXDescriptionAttribute)
                        if d and len(d) > 100:
                            return element

    children = ax_attr(element, kAXChildrenAttribute) or []
    for child in children:
        result = find_conversation_area(child, depth + 1)
        if result:
            return result
    return None


def main():
    ax_app, ns_app = find_chatgpt_app()
    if not ax_app:
        print("ChatGPT not found", file=sys.stderr)
        sys.exit(1)

    # Get first window
    windows = ax_attr(ax_app, "AXWindows")
    if not windows:
        print("No windows found", file=sys.stderr)
        sys.exit(1)

    print("Capturing window AX tree...", file=sys.stderr)
    tree = serialize_element(windows[0], max_depth=12)

    # Output JSON to stdout
    print(json.dumps(tree, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
