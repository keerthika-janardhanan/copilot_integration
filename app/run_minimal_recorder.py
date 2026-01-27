"""
Minimal Recorder: Captures page URL + element HTML + Playwright selectors
Uses CDP (Chrome DevTools Protocol) for multi-tab support like playwright codegen
No JavaScript injection - uses native browser events
"""

import argparse
import json
import signal
import sys
import time
import threading
from datetime import datetime
from pathlib import Path
from collections import deque
from playwright.sync_api import sync_playwright, Page

# Simplified injection - no binding, uses localStorage for communication
MINIMAL_INJECT = """
(() => {
    if (window.__minRecInstalled) return;
    window.__minRecInstalled = true;
    
    const actions = [];
    
    const getSelector = (el) => {
        if (el.id) return `#${el.id}`;
        if (el.name) return `[name="${el.name}"]`;
        let path = [];
        while (el && el.nodeType === 1) {
            let selector = el.nodeName.toLowerCase();
            if (el.id) {
                selector += `#${el.id}`;
                path.unshift(selector);
                break;
            }
            if (el.className) {
                selector += '.' + el.className.trim().split(/\\s+/).join('.');
            }
            path.unshift(selector);
            el = el.parentElement;
        }
        return path.join(' > ');
    };
    
    const getXPath = (el) => {
        if (el.id) return `//*[@id="${el.id}"]`;
        const parts = [];
        while (el && el.nodeType === 1) {
            let index = 1;
            let sibling = el.previousSibling;
            while (sibling) {
                if (sibling.nodeType === 1 && sibling.tagName === el.tagName) index++;
                sibling = sibling.previousSibling;
            }
            parts.unshift(`${el.tagName.toLowerCase()}[${index}]`);
            el = el.parentElement;
        }
        return '/' + parts.join('/');
    };
    
    const getRole = (el) => {
        const role = el.getAttribute('role');
        if (role) return role;
        const tag = el.tagName.toLowerCase();
        const type = (el.getAttribute('type') || '').toLowerCase();
        if (tag === 'button' || (tag === 'input' && ['button','submit','reset'].includes(type))) return 'button';
        if (tag === 'a' && el.getAttribute('href')) return 'link';
        if (tag === 'input' && type === 'text') return 'textbox';
        if (tag === 'input' && type === 'checkbox') return 'checkbox';
        if (tag === 'textarea') return 'textbox';
        if (tag === 'select') return 'combobox';
        return '';
    };
    
    const getAccessibleName = (el) => {
        const ariaLabel = el.getAttribute('aria-label');
        if (ariaLabel) return ariaLabel;
        const placeholder = el.getAttribute('placeholder');
        if (placeholder) return placeholder;
        const title = el.getAttribute('title');
        if (title) return title;
        const text = (el.innerText || el.textContent || '').trim();
        if (text) return text.slice(0, 100);
        return '';
    };
    
    const capture = (action, target) => {
        if (!target || target.nodeType !== 1) return;
        
        const role = getRole(target);
        const name = getAccessibleName(target);
        const selectors = {};
        
        if (role && name) {
            selectors.byRole = `getByRole('${role}', { name: '${name.replace(/'/g, "\\\\'")}' })`;
        }
        
        const ariaLabel = target.getAttribute('aria-label');
        if (ariaLabel) {
            selectors.byLabel = `getByLabel('${ariaLabel.replace(/'/g, "\\\\'")}')`;
        }
        
        const text = (target.innerText || '').trim();
        if (text && text.length < 100) {
            selectors.byText = `getByText('${text.replace(/'/g, "\\\\'")}')`;
        }
        
        const placeholder = target.getAttribute('placeholder');
        if (placeholder) {
            selectors.byPlaceholder = `getByPlaceholder('${placeholder.replace(/'/g, "\\\\'")}')`;
        }
        
        const testId = target.getAttribute('data-testid') || target.getAttribute('data-test-id');
        if (testId) {
            selectors.byTestId = `getByTestId('${testId}')`;
        }
        
        actions.push({
            action: action,
            timestamp: Date.now(),
            pageUrl: window.location.href,
            pageTitle: document.title,
            element: {
                html: target.outerHTML,
                selector: {
                    css: getSelector(target),
                    xpath: getXPath(target),
                    playwright: selectors
                }
            }
        });
    };
    
    // Store actions in window for polling
    window.__getRecordedActions = () => {
        const result = actions.slice();
        actions.length = 0;
        return result;
    };
    
    document.addEventListener('click', (e) => capture('click', e.target), { capture: true, passive: true });
    document.addEventListener('input', (e) => capture('input', e.target), { capture: true, passive: true });
    document.addEventListener('change', (e) => capture('change', e.target), { capture: true, passive: true });
    
    // Capture submit events (for forms)
    document.addEventListener('submit', (e) => {
        capture('click', e.target.querySelector('[type="submit"], button[type="submit"], button:not([type])')  || e.target);
    }, { capture: true, passive: true });
    
    // Backup: capture mousedown before navigation
    document.addEventListener('mousedown', (e) => {
        const target = e.target;
        // If it's a submit button or link, capture immediately
        if (target.type === 'submit' || target.tagName === 'BUTTON' || (target.tagName === 'A' && target.href)) {
            capture('click', target);
        }
    }, { capture: true, passive: true });
})();
"""


def main():
    parser = argparse.ArgumentParser(description='Minimal Recorder: page URL + element HTML + Playwright selectors')
    parser.add_argument('--url', required=True, help='Starting URL')
    parser.add_argument('--output-dir', default='recordings', help='Output directory')
    parser.add_argument('--session-name', default=None, help='Session name (default: timestamp)')
    parser.add_argument('--browser', default='chromium', choices=['chromium', 'firefox', 'webkit'])
    parser.add_argument('--headless', action='store_true', help='Run in headless mode')
    parser.add_argument('--timeout', type=int, default=None, help='Auto-stop after N seconds')
    
    args = parser.parse_args()
    
    # Setup output directory
    output_root = Path(args.output_dir).resolve()
    output_root.mkdir(parents=True, exist_ok=True)
    
    session_name = args.session_name or datetime.now().strftime("%Y%m%d_%H%M%S")
    session_dir = output_root / session_name
    session_dir.mkdir(parents=True, exist_ok=True)
    
    output_path = session_dir / 'metadata.json'
    
    recording = {
        'metadataVersion': '2025.minimal',
        'flowId': session_name,
        'startTime': datetime.now().isoformat(),
        'startUrl': args.url,
        'browser': args.browser,
        'actions': [],
        'pages': {}
    }
    
    print(f"[Minimal Recorder] Session: {session_name}")
    print(f"[Minimal Recorder] URL: {args.url}")
    print(f"[Minimal Recorder] Output: {output_path}")
    print(f"[Minimal Recorder] Press Ctrl+C to stop\n")
    
    pw = sync_playwright().start()
    browser = getattr(pw, args.browser).launch(headless=args.headless)
    context = browser.new_context()
    
    # Queue for thread-safe action capture
    action_queue = deque()
    queue_lock = threading.Lock()
    stop_event = threading.Event()
    write_lock = threading.Lock()
    
    # Background writer thread
    def background_writer():
        """Continuously write actions to metadata.json in background"""
        last_write = 0
        while not stop_event.is_set():
            time.sleep(1)  # Write every 1 second
            
            # Check if there are new actions
            with write_lock:
                if len(recording['actions']) > last_write:
                    try:
                        output_path.write_text(json.dumps(recording, indent=2), encoding='utf-8')
                        last_write = len(recording['actions'])
                    except Exception as e:
                        print(f"[Error] Background write failed: {e}")
    
    writer_thread = threading.Thread(target=background_writer, daemon=True)
    writer_thread.start()
    
    # Track all pages
    active_pages = {}
    page_counter = [0]
    
    def get_page_id(page):
        """Get or create page ID"""
        page_key = id(page)
        if page_key not in active_pages:
            page_counter[0] += 1
            page_id = f"page-{page_counter[0]}"
            active_pages[page_key] = {
                'pageId': page_id,
                'url': page.url,
                'title': '',
                'openedAt': datetime.now().isoformat()
            }
            recording['pages'][page_id] = active_pages[page_key]
            print(f"[NEW TAB] {page_id}: {page.url}")
        return active_pages[page_key]['pageId']
    
    def poll_page_actions(page: Page):
        """Poll actions from a page"""
        try:
            actions = page.evaluate('() => window.__getRecordedActions ? window.__getRecordedActions() : []')
            if actions:
                page_id = get_page_id(page)
                for action in actions:
                    action['pageId'] = page_id
                    with queue_lock:
                        action_queue.append(action)
        except Exception:
            pass
    
    def setup_page(page: Page):
        """Setup recorder on a page - inject AFTER load"""
        try:
            # DO NOT use add_init_script - it blocks new tabs
            # page.add_init_script(MINIMAL_INJECT)
            
            def on_load():
                try:
                    page_id = get_page_id(page)
                    active_pages[id(page)]['url'] = page.url
                    active_pages[id(page)]['title'] = page.title()
                    recording['pages'][page_id] = active_pages[id(page)]
                    print(f"[LOADED] {page_id}: {page.url}")
                    
                    # Inject script after load
                    try:
                        page.evaluate(MINIMAL_INJECT)
                    except Exception:
                        pass
                except Exception as e:
                    print(f"[Error] on_load: {e}")
            
            page.on('load', on_load)
            
        except Exception as e:
            print(f"[Error] setup_page: {e}")
    
    # DO NOT add init script at context level - it blocks new tabs
    # context.add_init_script(MINIMAL_INJECT)
    
    # Handle new pages/tabs/popups - MUST be non-blocking
    def on_page(page: Page):
        page_id = get_page_id(page)
        print(f"[NEW TAB] {page_id} - URL: {page.url}")
        setup_page(page)
        
        # Inject script in background - don't block
        def inject_async():
            try:
                # Wait for page to be ready
                page.wait_for_load_state('domcontentloaded', timeout=30000)
                print(f"[TAB LOADED] {page_id}: {page.url}")
                # Inject script
                page.evaluate(MINIMAL_INJECT)
                print(f"[TAB READY] {page_id}")
            except Exception as e:
                print(f"[TAB ERROR] {page_id}: {e}")
        
        threading.Thread(target=inject_async, daemon=True).start()
    
    context.on('page', on_page)
    
    # Create initial page
    page = context.new_page()
    setup_page(page)
    
    # Navigate
    try:
        page.goto(args.url, wait_until='domcontentloaded', timeout=30000)
        print(f"[LOADED] {page.url}\n")
    except Exception as e:
        print(f"[Error] Navigation failed: {e}")
    
    # Signal handler
    def signal_handler(sig, frame):
        stop_event.set()
    
    signal.signal(signal.SIGINT, signal_handler)
    try:
        signal.signal(signal.SIGTERM, signal_handler)
    except (AttributeError, ValueError):
        pass
    
    # Main loop
    start = time.time()
    try:
        while not stop_event.is_set():
            # Poll all active pages for actions
            for page_key in list(active_pages.keys()):
                try:
                    # Find the page object
                    for p in context.pages:
                        if id(p) == page_key:
                            poll_page_actions(p)
                            break
                except Exception:
                    pass
            
            # Drain action queue
            while True:
                with queue_lock:
                    if not action_queue:
                        break
                    payload = action_queue.popleft()
                
                with write_lock:
                    recording['actions'].append(payload)
                
                action = payload.get('action', '')
                url = payload.get('pageUrl', '')
                page_id = payload.get('pageId', '')
                print(f"[{action.upper()}] [{page_id}] {url}")
            
            time.sleep(0.2)
            
            if args.timeout and (time.time() - start) >= args.timeout:
                print(f"\n[Minimal Recorder] Timeout reached ({args.timeout}s)")
                stop_event.set()
                break
                
    except KeyboardInterrupt:
        print("\n[Minimal Recorder] Stopping...")
        stop_event.set()
    
    # Final drain
    time.sleep(0.3)
    while action_queue:
        with queue_lock:
            if not action_queue:
                break
            payload = action_queue.popleft()
        with write_lock:
            recording['actions'].append(payload)
    
    # Finalize
    recording['endTime'] = datetime.now().isoformat()
    recording['totalActions'] = len(recording['actions'])
    recording['totalPages'] = len(recording['pages'])
    
    # Final write
    with write_lock:
        output_path.write_text(json.dumps(recording, indent=2), encoding='utf-8')
    
    browser.close()
    pw.stop()
    
    print(f"\n[Minimal Recorder] Stopped")
    print(f"[Minimal Recorder] Captured {len(recording['actions'])} actions across {len(recording['pages'])} pages")
    print(f"[Minimal Recorder] Saved to: {output_path}")


if __name__ == '__main__':
    main()
