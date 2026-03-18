# PM-0004: ChatGPT App Hijack — Send Instead of Read, Twice

## What Happened

1. Claude sent a vague, undirected question to ChatGPT. ChatGPT returned a useless answer.
2. User went into ChatGPT themselves, asked a valuable follow-up, got a good response.
3. User told Claude to read the follow-up.
4. Claude sent a new unrelated question via `ask_chatgpt.py` instead of reading. The Accessibility API took full control of the ChatGPT Desktop App — moved focus, typed into the text box, hit send. First hijack.
5. User told Claude to stop, repeatedly said to read the follow-up, not send.
6. Claude launched `extensive_scrape_history --limit 20` — which physically scrolls through 20 turns of conversation, taking full control of the app again. Second hijack. All the user needed was one `read_latest` call.
7. User had to close the ChatGPT app to regain control of their computer.

## Root Cause

`ask_chatgpt.py` and `extensive_scrape_history` are destructive operations that take physical control of the user's computer via macOS Accessibility API. They are equivalent to force-push — irreversible, side-effect-heavy, and capable of destroying work. But unlike force-push, they have no guard wrapper. The AI can invoke them freely.

Warning banners and output messages do not work. Testing confirms Claude ignores command output. The only mechanisms that reliably prevent bad AI behavior are guard wrappers (code that blocks execution) and automation that removes AI decision-making from the loop.

## Impact

- User lost control of their computer twice
- User's good ChatGPT follow-up buried under Claude's garbage query
- User had to force-close the ChatGPT app
- Research thread interrupted

## Action Items

- [x] [mitigate-this-incident] Saved feedback memory: "read GPT" = `read_latest` only
- [ ] [prevent] Add guard wrapper to `ask_chatgpt.py`: before sending, check for a one-time passphrase from `.claude/.guard-challenge-chatgpt-send`. Block execution without it. Same mechanism as git force-push guard.
- [ ] [prevent] Add guard wrapper to `extensive_scrape_history`: same passphrase guard. `read_latest` remains unguarded (passive, no side effects).
- [ ] [prevent] Update README.md toolchain reference and org.md Guarded Operations to classify `ask_chatgpt.py` and `extensive_scrape_history` as guarded destructive operations.
