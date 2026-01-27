const express = require('express');
const bodyParser = require('body-parser');

const app = express();
app.use(bodyParser.json());

app.post('/api/copilot/chat', async (req, res) => {
    const timestamp = new Date().toISOString();
    console.log(`[${timestamp}] Request received`);
    
    try {
        const { messages } = req.body;
        const prompt = messages[0].content;
        
        // Mock response - replace with actual Copilot API call
        const response = `[MOCK RESPONSE - NOT REAL COPILOT] Response for: ${prompt.substring(0, 50)}...`;
        
        console.log(`[${timestamp}] SUCCESS: Mock response sent`);
        res.json({ content: response });
    } catch (error) {
        console.log(`[${timestamp}] ERROR: ${error.message}`);
        res.status(500).json({ error: error.message });
    }
});

const PORT = 3030;
app.listen(PORT, () => {
    console.log(`\n========================================`);
    console.log(`[MOCK SERVER] Running on http://localhost:${PORT}`);
    console.log(`========================================`);
    console.log('⚠️  Using MOCK responses (not real Copilot)');
    console.log('To use real Copilot:');
    console.log('1. Open vscode-copilot-bridge folder in VS Code');
    console.log('2. Press F5 to launch extension');
    console.log('3. Stop this mock server');
    console.log(`========================================\n`);
});
