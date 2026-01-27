# How to Verify Copilot API Usage

## Check Logs

### 1. Backend Console (Python)
Look for these messages when LLM is called:
```
[COPILOT] Sending request to http://localhost:3030/api/copilot/chat
[COPILOT] ✓ Response received (status: 200)
```

If you see errors:
```
[COPILOT] ✗ Error: Connection refused
```
→ VS Code extension not running

### 2. VS Code Debug Console
When extension is running (F5), you'll see:
```
[COPILOT BRIDGE] Extension activated
[COPILOT BRIDGE] Server running on http://localhost:3030
[2024-01-15T10:30:45.123Z] Copilot request received
[2024-01-15T10:30:45.123Z] Using model: gpt-4
[2024-01-15T10:30:47.456Z] SUCCESS: Response length: 1234 chars
```

### 3. Test Manually
```bash
curl -X POST http://localhost:3030/api/copilot/chat -H "Content-Type: application/json" -d "{\"messages\":[{\"role\":\"user\",\"content\":\"Say hello\"}]}"
```

Should return:
```json
{"content":"Hello! How can I help you?"}
```

## What to Look For

**✓ Using Copilot:**
- Backend shows `[COPILOT]` logs
- VS Code Debug Console shows timestamps
- Responses come from `localhost:3030`

**✗ Fallback/Error:**
- `Connection refused` errors
- No logs in VS Code Debug Console
- Extension not running (check VS Code status bar)

## Quick Check
Run this in your UI and watch the backend console - you should see `[COPILOT]` messages appear in real-time.
