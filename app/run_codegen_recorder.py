"""
Codegen-based Recorder: Wraps `playwright codegen` to capture metadata without inspector UI
Parses codegen output to extract selectors + captures page context
"""

import argparse
import json
import subprocess
import threading
import time
import re
from datetime import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright


def main():
    parser = argparse.ArgumentParser(description='Codegen-based Recorder')
    parser.add_argument('--url', required=True)
    parser.add_argument('--output-dir', default='recordings')
    parser.add_argument('--session-name', default=None)
    parser.add_argument('--browser', default='chromium', choices=['chromium', 'firefox', 'webkit'])
    parser.add_argument('--headless', action='store_true')
    parser.add_argument('--timeout', type=int, default=None)
    
    args = parser.parse_args()
    
    output_root = Path(args.output_dir).resolve()
    output_root.mkdir(parents=True, exist_ok=True)
    
    session_name = args.session_name or datetime.now().strftime("%Y%m%d_%H%M%S")
    session_dir = output_root / session_name
    session_dir.mkdir(parents=True, exist_ok=True)
    
    # Temp file for codegen output
    codegen_output = session_dir / 'codegen_raw.txt'
    metadata_output = session_dir / 'metadata.json'
    
    recording = {
        'metadataVersion': '2025.codegen',
        'flowId': session_name,
        'startTime': datetime.now().isoformat(),
        'startUrl': args.url,
        'browser': args.browser,
        'actions': [],
        'codegenRaw': ''
    }
    
    print(f"[Codegen Recorder] Session: {session_name}")
    print(f"[Codegen Recorder] Starting playwright codegen (inspector hidden)")
    print(f"[Codegen Recorder] Interact with browser, press Ctrl+C to stop\n")
    
    # Run playwright codegen and capture output
    cmd = [
        'playwright', 'codegen',
        '--target', 'python-pytest',
        '--browser', args.browser,
        args.url
    ]
    
    if args.headless:
        print("[Warning] Codegen doesn't support headless, running headed")
    
    try:
        # Start codegen process
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        
        output_lines = []
        
        def read_output():
            for line in process.stdout:
                output_lines.append(line)
                print(f"[CODEGEN] {line.rstrip()}")
        
        thread = threading.Thread(target=read_output, daemon=True)
        thread.start()
        
        # Wait for process or timeout
        start = time.time()
        while process.poll() is None:
            time.sleep(0.5)
            if args.timeout and (time.time() - start) >= args.timeout:
                print(f"\n[Codegen Recorder] Timeout ({args.timeout}s)")
                process.terminate()
                break
        
        thread.join(timeout=1)
        
        # Parse codegen output
        codegen_text = ''.join(output_lines)
        recording['codegenRaw'] = codegen_text
        
        # Extract actions from codegen output
        # Look for page.goto, page.click, page.fill, etc.
        action_patterns = [
            (r'page\.goto\(["\']([^"\']*)["\'']\)', 'navigate'),
            (r'page\.click\(["\']([^"\']*)["\'']\)', 'click'),
            (r'page\.fill\(["\']([^"\']*)["\''],\s*["\']([^"\']*)["\'']\)', 'fill'),
            (r'page\.get_by_role\(["\']([^"\']*)["\''].*?name=["\']([^"\']*)["\'']\)', 'byRole'),
            (r'page\.get_by_label\(["\']([^"\']*)["\'']\)', 'byLabel'),
            (r'page\.get_by_text\(["\']([^"\']*)["\'']\)', 'byText'),
            (r'page\.get_by_placeholder\(["\']([^"\']*)["\'']\)', 'byPlaceholder'),
        ]
        
        for pattern, action_type in action_patterns:
            for match in re.finditer(pattern, codegen_text):
                recording['actions'].append({
                    'action': action_type,
                    'selector': match.group(0),
                    'timestamp': datetime.now().isoformat()
                })
        
    except KeyboardInterrupt:
        print("\n[Codegen Recorder] Stopping...")
        if process.poll() is None:
            process.terminate()
    except Exception as e:
        print(f"[Error] {e}")
    
    # Save
    recording['endTime'] = datetime.now().isoformat()
    recording['totalActions'] = len(recording['actions'])
    
    metadata_output.write_text(json.dumps(recording, indent=2), encoding='utf-8')
    codegen_output.write_text(recording['codegenRaw'], encoding='utf-8')
    
    print(f"\n[Codegen Recorder] Captured {len(recording['actions'])} actions")
    print(f"[Codegen Recorder] Saved: {metadata_output}")


if __name__ == '__main__':
    main()
