import sys
import shutil
from pathlib import Path

def switch_to_copilot():
    """Switch to Copilot LLM client"""
    llm_client = Path("app/llm_client.py")
    backup = Path("app/llm_client_azure_backup.py")
    copilot = Path("app/llm_client_copilot.py")
    
    if not backup.exists():
        shutil.copy(llm_client, backup)
        print("✓ Backed up Azure OpenAI client")
    
    shutil.copy(copilot, llm_client)
    print("✓ Switched to Copilot client")
    print("\nNext steps:")
    print("1. Install VS Code extension from vscode-copilot-bridge/")
    print("2. Run: cd vscode-copilot-bridge && npm install && npm run compile")
    print("3. Press F5 in VS Code to launch extension")
    print("4. Set COPILOT_BRIDGE_URL=http://localhost:3030 in .env")

def switch_to_azure():
    """Switch back to Azure OpenAI client"""
    llm_client = Path("app/llm_client.py")
    backup = Path("app/llm_client_azure_backup.py")
    
    if backup.exists():
        shutil.copy(backup, llm_client)
        print("✓ Switched back to Azure OpenAI client")
    else:
        print("✗ No backup found")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python switch_llm.py [copilot|azure]")
        sys.exit(1)
    
    mode = sys.argv[1].lower()
    if mode == "copilot":
        switch_to_copilot()
    elif mode == "azure":
        switch_to_azure()
    else:
        print("Invalid mode. Use 'copilot' or 'azure'")
