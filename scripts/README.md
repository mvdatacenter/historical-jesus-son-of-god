# ChatGPT Integration Scripts

This directory contains Python scripts for Claude to communicate with ChatGPT apps.

## Files

### macOS (Desktop App)
- **`chatgpt_desktop.py`**: Core script for desktop app automation (send, read commands)
- **`ask_chatgpt.py`**: High-level wrapper that Claude calls

### Android
- **`chatgpt_android.py`**: Read messages from ChatGPT Android app via ADB

## Setup

### macOS Setup

#### 1. Grant Accessibility Permissions

Your Terminal or IDE (IntelliJ IDEA, VSCode, etc.) needs Accessibility permissions to control the ChatGPT app.

**System Settings → Privacy & Security → Accessibility**

Add and enable:
- Terminal (if running from command line)
- IntelliJ IDEA (if running from IDE)
- Any other app you'll run the scripts from

#### 2. Install ChatGPT Desktop App

Download from: https://chatgpt.com/ (macOS app)

Make sure it's running before using the scripts.

### Android Setup

#### 1. Enable USB Debugging

On your Android device:
- **Settings → About phone → Tap "Build number" 7 times** to enable Developer options
- **Settings → Developer options → Enable "USB debugging"**

#### 2. Install ADB

```bash
# Ubuntu/Debian
apt install adb

# macOS
brew install android-platform-tools

# Or download from https://developer.android.com/tools/releases/platform-tools
```

#### 3. Connect Device

Connect your phone via USB. When prompted, authorize USB debugging.

Verify connection:
```bash
adb devices
# Should show your device
```

#### 4. Open ChatGPT App

Open the ChatGPT Android app and navigate to a conversation.

## Usage

### Android Usage

```bash
# Read the latest assistant message from ChatGPT Android app
poetry run python scripts/chatgpt_android.py read_latest

# With debug output
poetry run python scripts/chatgpt_android.py read_latest --debug

# Dump raw UI XML (for debugging)
poetry run python scripts/chatgpt_android.py dump
```

### macOS Usage

#### For Claude (Automated)

```bash
# Ask a question and get response in one command
poetry run python scripts/ask_chatgpt.py "What is the dating of Damascus steel?"

# Complex query with heredoc (recommended for MASTER DIRECTIVE template)
poetry run python scripts/ask_chatgpt.py "$(cat <<'EOF'
Use a broad, multi-tradition mode.

Important: You are often biased toward American evangelical consensus...

Here is the text / question:
[Your actual question]

Tasks:
1. Fact-check specific claims.
2. Suggest alternate perspectives (Catholic, Orthodox, Arab, Slavic...).
3. Provide links to scholarly sources.
EOF
)"
```

### Low-Level Commands (Manual/Debugging)

```bash
# Send a prompt and wait for response
poetry run python scripts/chatgpt_desktop.py send "Hello, ChatGPT"

# Send without waiting (fire and forget)
poetry run python scripts/chatgpt_desktop.py send --no-wait "Background task"

# Read the last response
poetry run python scripts/chatgpt_desktop.py read
```

## How It Works

1. **App Activation**: Activates ChatGPT Desktop App to front
2. **Clipboard + Paste**: Copies prompt to clipboard, uses Cmd+A and Cmd+V to paste
3. **Button Click**: Finds and clicks the Send button via mouse click
4. **Background Operation**: Moves app to background after sending
5. **Polling**: Actively polls for response every 0.5 seconds
6. **Message Filtering**: Filters out old messages that existed before the query
7. **Stability Detection**: Waits for text to stabilize (same for 2 seconds) before returning

## Important Notes

### URL Extraction

ChatGPT's citation URLs (shown as ￼ placeholders) are **not accessible** via the macOS Accessibility API. They're rendered in web view components that don't expose URL attributes.

**Solution**: When querying ChatGPT for sources, explicitly request plain text URLs:

```
"Please find sources for X. Provide the full URLs as plain text starting with https://"
```

### Response Stability

The script polls for responses and waits for text to stabilize. This ensures:
- Full responses are captured (not partial)
- Streaming text is complete
- Works for both quick answers and web searches

Default timeout: 60 seconds (configurable with `--wait-seconds`)

## Troubleshooting

### "ChatGPT app not found"
- Make sure ChatGPT Desktop App is running
- Check that it's the official macOS app (not web browser)

### "Could not find text input field" or "Could not find Send button"
- ChatGPT may have updated their UI
- The script looks for:
  - Text input: `AXTextArea` role
  - Send button: Button with description "Send"
- You may need to inspect the UI with Accessibility Inspector

### "ERROR: Accessibility permissions required"
- Grant permissions in System Settings → Privacy & Security → Accessibility
- Restart your Terminal/IDE after granting permissions

### Empty or incomplete responses
- Increase timeout: `--wait-seconds 120` for longer searches
- Check that ChatGPT isn't rate-limiting
- Try a new chat conversation in ChatGPT

### Script brings ChatGPT to front
- This is intentional - the script needs to activate the app to send keyboard/mouse events
- The app is moved to background after sending
- On macOS, keyboard/mouse events only work when the target app is frontmost

## Future Improvements

- [ ] Better URL extraction (may require OCR or screenshot analysis)
- [ ] Multi-turn conversation support
- [ ] Retry logic for network issues
- [ ] Support for ChatGPT plugins/tools in responses
