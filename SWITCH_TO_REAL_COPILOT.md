# Switch from Mock to Real Copilot

## Current State
✓ Backend running (port 8001)
✓ Frontend running (port 5178)
✓ Mock bridge running (port 3030)

## To Use Real Copilot:

### Step 1: Stop Mock Server
Close the window running `node copilot-bridge-server.js`

### Step 2: Open VS Code Extension
```bash
cd vscode-copilot-bridge
code .
```

### Step 3: Run Extension
In VS Code menu: Run → Start Debugging (or press F5)

A new VS Code window opens - this is the extension host.

### Step 4: Verify
Check Debug Console (View → Debug Console):
```
[COPILOT BRIDGE] Extension activated
[COPILOT BRIDGE] Server running on http://localhost:3030
```

### Step 5: Test
Use your UI - responses will now come from real GitHub Copilot.

## Troubleshooting

**"Copilot not available"**
- Install GitHub Copilot extension in VS Code
- Sign in to GitHub (Accounts icon, bottom left)
- Verify Copilot subscription is active

**Can't press F5**
- Use menu: Run → Start Debugging
- Or Ctrl+Shift+D, then click green play button

**Port 3030 already in use**
- Make sure mock server is stopped
- Check: `netstat -ano | findstr :3030`
