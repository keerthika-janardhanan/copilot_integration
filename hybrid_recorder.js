const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

/**
 * Hybrid Recorder - Captures Playwright actions + DOM element details
 * Output: JSON file with page details and element HTML only
 */

async function startHybridRecording(startUrl = 'about:blank', outputDir = 'recordings') {
  // Create output directory
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  const outputFile = path.join(outputDir, `recording_${timestamp}.json`);

  const browser = await chromium.launch({ 
    headless: false,
    args: ['--start-maximized']
  });
  
  const context = await browser.newContext({
    viewport: null,
    recordVideo: undefined,
    recordHar: undefined
  });
  
  const page = await context.newPage();

  // Hide Playwright inspector by setting environment variable
  process.env.PWDEBUG = '0';
  
  // Disable inspector toolbar
  await page.addInitScript(() => {
    // Remove Playwright inspector if it appears
    const observer = new MutationObserver(() => {
      const inspector = document.querySelector('[data-testid="playwright-inspector"]');
      if (inspector) inspector.remove();
      
      const toolbar = document.querySelector('.playwright-inspector');
      if (toolbar) toolbar.remove();
    });
    observer.observe(document.documentElement, { childList: true, subtree: true });
  });

  const recording = {
    startTime: new Date().toISOString(),
    startUrl: startUrl,
    actions: []
  };

  console.log('\n=== Hybrid Recorder Started ===');
  console.log(`Output file: ${outputFile}`);
  console.log('Interact with the page. Close browser to stop recording.\n');

  // Navigate to start URL
  if (startUrl !== 'about:blank') {
    await page.goto(startUrl);
  }

  // Capture page navigation
  page.on('framenavigated', async (frame) => {
    if (frame === page.mainFrame()) {
      const action = {
        type: 'navigation',
        timestamp: new Date().toISOString(),
        page: {
          url: page.url(),
          title: await page.title().catch(() => '')
        }
      };
      recording.actions.push(action);
      console.log(`[NAV] ${action.page.url}`);
    }
  });

  // Inject element capture script
  await context.addInitScript(() => {
    // Helper to generate CSS selector
    function generateCSSSelector(element) {
      if (element.id) return `#${element.id}`;
      
      let selector = element.tagName.toLowerCase();
      
      if (element.className && typeof element.className === 'string') {
        const classes = element.className.trim().split(/\s+/).filter(c => c);
        if (classes.length > 0) {
          selector += '.' + classes.join('.');
        }
      }
      
      return selector;
    }

    // Helper to generate XPath
    function generateXPath(element) {
      if (element.id) return `//*[@id="${element.id}"]`;
      
      const parts = [];
      let current = element;
      
      while (current && current.nodeType === Node.ELEMENT_NODE) {
        let index = 1;
        let sibling = current.previousSibling;
        
        while (sibling) {
          if (sibling.nodeType === Node.ELEMENT_NODE && sibling.tagName === current.tagName) {
            index++;
          }
          sibling = sibling.previousSibling;
        }
        
        const tagName = current.tagName.toLowerCase();
        const part = index > 1 ? `${tagName}[${index}]` : tagName;
        parts.unshift(part);
        
        current = current.parentElement;
      }
      
      return '/' + parts.join('/');
    }

    // Capture element details
    window.__captureElement = (eventType, element) => {
      const elementData = {
        type: eventType,
        timestamp: new Date().toISOString(),
        page: {
          url: window.location.href,
          title: document.title
        },
        element: {
          html: element.outerHTML,
          tagName: element.tagName,
          id: element.id || '',
          className: element.className || '',
          text: element.textContent?.trim().substring(0, 200) || '',
          attributes: {}
        },
        selectors: {
          css: generateCSSSelector(element),
          xpath: generateXPath(element)
        }
      };

      // Capture key attributes
      if (element.attributes) {
        for (let attr of element.attributes) {
          elementData.element.attributes[attr.name] = attr.value;
        }
      }

      return elementData;
    };

    // Listen to clicks with capture phase to catch all clicks
    document.addEventListener('click', (e) => {
      const data = window.__captureElement('click', e.target);
      window.__recordedActions = window.__recordedActions || [];
      window.__recordedActions.push(data);
      console.log('[RECORDER] Click captured:', e.target.tagName, e.target.id || e.target.className);
    }, { capture: true, passive: true });

    // Also listen to mousedown as backup for fast clicks
    document.addEventListener('mousedown', (e) => {
      // Store mousedown target to compare with click
      window.__lastMouseDown = { target: e.target, time: Date.now() };
    }, { capture: true, passive: true });

    // Listen to submit events (for forms)
    document.addEventListener('submit', (e) => {
      const data = window.__captureElement('submit', e.target);
      window.__recordedActions = window.__recordedActions || [];
      window.__recordedActions.push(data);
      console.log('[RECORDER] Submit captured:', e.target.tagName);
    }, { capture: true, passive: true });

    // Listen to input/change with debouncing
    let inputTimeout;
    document.addEventListener('input', (e) => {
      clearTimeout(inputTimeout);
      inputTimeout = setTimeout(() => {
        const data = window.__captureElement('input', e.target);
        window.__recordedActions = window.__recordedActions || [];
        window.__recordedActions.push(data);
      }, 300); // Debounce 300ms
    }, { capture: true, passive: true });

    // Listen to select changes
    document.addEventListener('change', (e) => {
      if (e.target.tagName === 'SELECT') {
        const data = window.__captureElement('select', e.target);
        window.__recordedActions = window.__recordedActions || [];
        window.__recordedActions.push(data);
      }
    }, true);
  });

  // Periodically collect recorded actions
  const collectInterval = setInterval(async () => {
    try {
      const actions = await page.evaluate(() => {
        const recorded = window.__recordedActions || [];
        window.__recordedActions = [];
        return recorded;
      });

      if (actions && actions.length > 0) {
        recording.actions.push(...actions);
        actions.forEach(action => {
          console.log(`[${action.type.toUpperCase()}] ${action.element.tagName} - ${action.element.text.substring(0, 50)}`);
        });
      }
    } catch (e) {
      // Page might be navigating, ignore
    }
  }, 1000);

  // Wait for browser to close
  await page.waitForEvent('close').catch(() => {});
  
  clearInterval(collectInterval);

  // Collect any remaining actions
  try {
    const finalActions = await page.evaluate(() => window.__recordedActions || []);
    if (finalActions.length > 0) {
      recording.actions.push(...finalActions);
    }
  } catch (e) {
    // Ignore
  }

  recording.endTime = new Date().toISOString();
  recording.totalActions = recording.actions.length;

  // Save recording
  fs.writeFileSync(outputFile, JSON.stringify(recording, null, 2));

  await browser.close();

  console.log('\n=== Recording Complete ===');
  console.log(`Total actions captured: ${recording.totalActions}`);
  console.log(`Saved to: ${outputFile}\n`);

  return outputFile;
}

// CLI
if (require.main === module) {
  const args = process.argv.slice(2);
  const url = args[0] || 'about:blank';
  const outputDir = args[1] || 'recordings';

  startHybridRecording(url, outputDir)
    .then(() => process.exit(0))
    .catch(err => {
      console.error('Error:', err);
      process.exit(1);
    });
}

module.exports = { startHybridRecording };
