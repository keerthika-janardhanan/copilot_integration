"""
Hybrid Recorder - Combines Playwright Codegen with DOM Element Capture
Captures: Page details + Element HTML (no HAR, trace, screenshot, full HTML)
"""

import subprocess
import json
import os
from pathlib import Path
from datetime import datetime


class HybridRecorder:
    def __init__(self, output_dir="recordings"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
    def start_recording(self, url=None, browser="chromium"):
        """Start hybrid recording session"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.output_dir / f"recording_{timestamp}.json"
        
        # Create custom recorder script
        recorder_script = self._create_recorder_script(output_file)
        script_path = self.output_dir / f"recorder_{timestamp}.js"
        
        with open(script_path, 'w') as f:
            f.write(recorder_script)
        
        # Start Playwright codegen with custom script
        cmd = [
            "npx", "playwright", "codegen",
            "--target", "javascript",
            "--save-storage", str(self.output_dir / f"storage_{timestamp}.json")
        ]
        
        if url:
            cmd.append(url)
        
        cmd.extend(["-b", browser])
        
        print(f"Starting hybrid recorder...")
        print(f"Output will be saved to: {output_file}")
        print(f"Close the browser window to stop recording.")
        
        subprocess.run(cmd)
        
        print(f"\nRecording saved to: {output_file}")
        return output_file
    
    def _create_recorder_script(self, output_file):
        """Create custom recorder script that captures element details"""
        return f"""
const {{ chromium }} = require('playwright');
const fs = require('fs');

(async () => {{
  const browser = await chromium.launch({{ headless: false }});
  const context = await browser.newContext();
  const page = await context.newPage();
  
  const recording = {{
    startTime: new Date().toISOString(),
    actions: []
  }};
  
  // Capture page navigation
  page.on('framenavigated', async (frame) => {{
    if (frame === page.mainFrame()) {{
      recording.actions.push({{
        type: 'navigation',
        timestamp: new Date().toISOString(),
        url: page.url(),
        title: await page.title()
      }});
    }}
  }});
  
  // Capture element interactions
  await page.exposeFunction('captureElement', async (elementInfo) => {{
    recording.actions.push(elementInfo);
  }});
  
  // Inject listener for all interactions
  await page.addInitScript(() => {{
    const captureInteraction = async (event, element) => {{
      const elementHTML = element.outerHTML;
      const pageInfo = {{
        url: window.location.href,
        title: document.title
      }};
      
      await window.captureElement({{
        type: event.type,
        timestamp: new Date().toISOString(),
        page: pageInfo,
        element: {{
          html: elementHTML,
          tagName: element.tagName,
          id: element.id,
          className: element.className,
          text: element.textContent?.trim().substring(0, 100)
        }},
        selector: {{
          css: generateCSSSelector(element),
          xpath: generateXPath(element)
        }}
      }});
    }};
    
    function generateCSSSelector(element) {{
      if (element.id) return `#${{element.id}}`;
      if (element.className) {{
        const classes = element.className.split(' ').filter(c => c).join('.');
        return `${{element.tagName.toLowerCase()}}.${{classes}}`;
      }}
      return element.tagName.toLowerCase();
    }}
    
    function generateXPath(element) {{
      if (element.id) return `//*[@id="${{element.id}}"]`;
      const parts = [];
      while (element && element.nodeType === Node.ELEMENT_NODE) {{
        let index = 0;
        let sibling = element.previousSibling;
        while (sibling) {{
          if (sibling.nodeType === Node.ELEMENT_NODE && sibling.tagName === element.tagName) {{
            index++;
          }}
          sibling = sibling.previousSibling;
        }}
        const tagName = element.tagName.toLowerCase();
        const pathIndex = index ? `[${{index + 1}}]` : '';
        parts.unshift(`${{tagName}}${{pathIndex}}`);
        element = element.parentNode;
      }}
      return parts.length ? `/${{parts.join('/')}}` : '';
    }}
    
    // Listen to clicks
    document.addEventListener('click', (e) => {{
      captureInteraction(e, e.target);
    }}, true);
    
    // Listen to input changes
    document.addEventListener('input', (e) => {{
      captureInteraction(e, e.target);
    }}, true);
    
    // Listen to form submissions
    document.addEventListener('submit', (e) => {{
      captureInteraction(e, e.target);
    }}, true);
  }});
  
  // Wait for user to close browser
  await page.waitForEvent('close').catch(() => {{}});
  
  recording.endTime = new Date().toISOString();
  
  // Save recording
  fs.writeFileSync('{output_file}', JSON.stringify(recording, null, 2));
  
  await browser.close();
}})();
"""


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Hybrid Recorder - Playwright + DOM Capture')
    parser.add_argument('--url', help='Starting URL', default=None)
    parser.add_argument('--browser', choices=['chromium', 'firefox', 'webkit'], default='chromium')
    parser.add_argument('--output-dir', default='recordings', help='Output directory')
    
    args = parser.parse_args()
    
    recorder = HybridRecorder(output_dir=args.output_dir)
    recorder.start_recording(url=args.url, browser=args.browser)


if __name__ == '__main__':
    main()
