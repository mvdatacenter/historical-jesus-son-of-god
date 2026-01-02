# ChatGPT Integration Scripts

This directory contains Python scripts for Claude to communicate with ChatGPT apps.

## Files

### macOS (Desktop App)
- **`chatgpt_desktop.py`**: Core script for desktop app automation (send, read commands)
- **`ask_chatgpt.py`**: High-level wrapper that Claude calls

### Android
- **`chatgpt_android.py`**: Read messages from ChatGPT Android app via Shizuku
- **`test_chatgpt_android.py`**: Unit tests (22 tests)

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

### Android Setup (Termux + Shizuku)

The Android script uses Shizuku to run uiautomator commands. Works from Termux/proot.

#### 1. Install Shizuku

Download from [GitHub Releases](https://github.com/RikkaApps/Shizuku/releases) (not Play Store - outdated).

#### 2. Enable Wireless Debugging

- **Settings → Developer options → Wireless debugging** → Enable

#### 3. Start Shizuku

Open Shizuku app → "Start via Wireless debugging" → Follow pairing instructions.

#### 4. Export rish to Termux

In Shizuku: **"Use Shizuku in terminal apps"** → Export files.

Then in Termux:
```bash
termux-setup-storage
cp ~/storage/shared/Documents/rish* $PREFIX/bin/
chmod +x $PREFIX/bin/rish
chmod 400 $PREFIX/bin/rish_shizuku.dex
```

#### 5. Configure rish for Termux

Edit `$PREFIX/bin/rish` and change `"PKG"` to `"com.termux"`:
```bash
sed -i 's/"PKG"/"com.termux"/' $PREFIX/bin/rish
```

#### 6. Fix for proot (if using proot-distro)

If running from proot, remove the permission check that fails due to proot faking permissions:
```bash
# Edit rish and remove/comment out the lines 10-21 (the -w check block)
```

#### 7. Verify Setup

```bash
python scripts/chatgpt_android.py test
```

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

### macOS

1. **App Activation**: Activates ChatGPT Desktop App to front
2. **Clipboard + Paste**: Copies prompt to clipboard, uses Cmd+A and Cmd+V to paste
3. **Button Click**: Finds and clicks the Send button via mouse click
4. **Background Operation**: Moves app to background after sending
5. **Polling**: Actively polls for response every 0.5 seconds
6. **Message Filtering**: Filters out old messages that existed before the query
7. **Stability Detection**: Waits for text to stabilize (same for 2 seconds) before returning

### Android

1. **App Switch**: Uses `am start` via Shizuku/rish to bring ChatGPT to foreground
2. **UI Dump**: Runs `uiautomator dump` to capture the screen hierarchy as XML
3. **Return to Termux**: Switches back to Termux automatically
4. **Message Extraction**: Parses XML with regex to extract message text
5. **Filtering**: Removes UI elements (buttons, labels) and short text

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
