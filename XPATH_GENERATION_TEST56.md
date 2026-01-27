# XPath Generation from Refined Ingestion - test56 Example

## Overview
After recording and refinement, XPaths are generated and stored in multiple formats for test script generation. The system uses a **selector priority hierarchy** to ensure robust test automation.

## test56 Recording Analysis

### Raw Recording Stats
- **Total actions captured**: 40+ actions
- **Duplicate actions**: ~25 (multiple input events on same field)
- **After deduplication**: ~15 unique actions
- **After auth filtering**: ~10 application-specific actions

### Refinement Process for test56

```
Raw metadata.json (40 actions)
    ↓
Sort by timestamp
    ↓
Filter auth steps (Okta, OneCognizant)
    ↓
Remove consecutive duplicates
    ↓
Convert to refined steps
    ↓
Save to app/generated_flows/test56-test56.refined.json
    ↓
Ingest into Vector DB with XPath metadata
```

## XPath Generation Strategy

### 1. Selector Priority Hierarchy

For each action, the system captures multiple selector types in priority order:

```python
Priority 1: Playwright Semantic Selectors
  - getByRole('button', { name: 'Next' })
  - getByLabel('date input')
  - getByText('ClaimCenter')
  - getByPlaceholder('MM/dd/yyyy')

Priority 2: Stable Selectors
  - CSS with ID: #FNOLWizard-Next
  - CSS with name: [name="Login-LoginScreen-LoginDV-username"]

Priority 3: XPath (Fallback)
  - Absolute: /html[1]/body[1]/form[1]/div[1]/div[2]/...
  - Relative: //*[@id="gw-center-panel"]
```

### 2. test56 XPath Examples

#### Example 1: Username Field (ClaimCenter Login)
```json
{
  "step": 1,
  "action": "Fill",
  "navigation": "Enter username",
  "locators": {
    "playwright": "",  // Empty - no semantic selector captured
    "stable": "[name=\"Login-LoginScreen-LoginDV-username\"]",
    "css": "[name=\"Login-LoginScreen-LoginDV-username\"]",
    "xpath": "/html[1]/body[1]/form[1]/div[1]/div[2]/div[2]/div[2]/div[1]/div[4]/div[4]/div[1]/div[2]/div[1]/div[1]/div[1]/div[2]/div[1]/div[1]/input[1]",
    "raw_xpath": "/html[1]/body[1]/form[1]/div[1]/div[2]/div[2]/div[2]/div[1]/div[4]/div[4]/div[1]/div[2]/div[1]/div[1]/div[1]/div[2]/div[1]/div[1]/input[1]"
  }
}
```

**Generated Test Script:**
```typescript
// Priority 1: Use CSS name selector (most stable)
await page.locator('[name="Login-LoginScreen-LoginDV-username"]').fill('superuser');

// Fallback: XPath if CSS fails
await page.locator('/html[1]/body[1]/form[1]//input[@name="Login-LoginScreen-LoginDV-username"]').fill('superuser');
```

#### Example 2: Date Input Field
```json
{
  "step": 2,
  "action": "Fill",
  "navigation": "Enter date input",
  "locators": {
    "playwright": "getByRole('textbox', { name: 'date input' })",
    "stable": "[name=\"FNOLWizard-FNOLWizard_FindPolicyScreen-FNOLWizardFindPolicyPanelSet-date\"]",
    "css": "[name=\"FNOLWizard-FNOLWizard_FindPolicyScreen-FNOLWizardFindPolicyPanelSet-date\"]",
    "xpath": "/html[1]/body[1]/form[1]/div[1]/div[2]/div[2]/div[2]/div[1]/div[5]/div[1]/div[1]/table[1]/tbody[1]/tr[1]/td[1]/div[1]/div[1]/div[1]/div[1]/div[11]/div[2]/div[1]/div[1]/input[1]",
    "role": "textbox",
    "labels": "date input"
  }
}
```

**Generated Test Script:**
```typescript
// Priority 1: Playwright semantic selector (most resilient)
await page.getByRole('textbox', { name: 'date input' }).fill('04/15/2024');

// Priority 2: CSS name selector
await page.locator('[name="FNOLWizard-FNOLWizard_FindPolicyScreen-FNOLWizardFindPolicyPanelSet-date"]').fill('04/15/2024');

// Priority 3: XPath fallback
await page.locator('//input[@aria-label="date input"]').fill('04/15/2024');
```

#### Example 3: Next Button
```json
{
  "step": 3,
  "action": "Click",
  "navigation": "Click the Next button",
  "locators": {
    "playwright": "getByRole('button', { name: 'Next' })",
    "stable": "div#FNOLWizard-Next > div.gw-action--inner.gw-hasDivider.gw-focus > div.gw-label",
    "css": "div#FNOLWizard-Next > div.gw-action--inner.gw-hasDivider.gw-focus > div.gw-label",
    "xpath": "/html[1]/body[1]/form[1]/div[1]/div[2]/div[2]/div[1]/div[5]/div[2]/div[4]/div[1]/div[2]",
    "role": "button",
    "labels": "Next"
  }
}
```

**Generated Test Script:**
```typescript
// Priority 1: Playwright semantic (best for maintainability)
await page.getByRole('button', { name: 'Next' }).click();

// Priority 2: CSS with ID
await page.locator('#FNOLWizard-Next').click();

// Priority 3: XPath
await page.locator('//div[@aria-label="Next"]').click();
```

#### Example 4: Combobox Selection
```json
{
  "step": 4,
  "action": "Fill",
  "navigation": "Select Loss Cause",
  "locators": {
    "playwright": "getByRole('combobox', { name: '<none>\\nAnimal\\nCollision...' })",
    "stable": "[name=\"FNOLWizard-FullWizardStepSet-FNOLWizard_NewLossDetailsScreen-LossDetailsAddressDV-Claim_LossCause\"]",
    "css": "[name=\"FNOLWizard-FullWizardStepSet-FNOLWizard_NewLossDetailsScreen-LossDetailsAddressDV-Claim_LossCause\"]",
    "xpath": "/html[1]/body[1]/form[1]/div[1]/div[2]/div[2]/div[2]/div[1]/div[3]/div[1]/div[1]/div[3]/div[2]/div[1]/div[1]/div[1]/select[1]",
    "role": "combobox"
  }
}
```

**Generated Test Script:**
```typescript
// Priority 1: CSS name selector (stable for Guidewire)
await page.locator('[name="FNOLWizard-FullWizardStepSet-FNOLWizard_NewLossDetailsScreen-LossDetailsAddressDV-Claim_LossCause"]').selectOption('fire');

// Priority 2: XPath with tag
await page.locator('//select[contains(@name, "Claim_LossCause")]').selectOption('fire');
```

## How XPaths Are Used in Test Script Generation

### 1. Vector DB Storage Format

Each refined step is stored in ChromaDB with this structure:

```python
{
  "id": "test56-s001",
  "content": {
    "summary": "test56 | Step 1: Fill\nNavigation: Enter username...",
    "payload": {
      "flow": "test56",
      "step_index": 1,
      "action": "fill",
      "locators": {
        "playwright": "",
        "stable": "[name='Login-LoginScreen-LoginDV-username']",
        "xpath": "/html[1]/body[1]/form[1]//input[1]",
        "css": "[name='Login-LoginScreen-LoginDV-username']",
        "role": "textbox",
        "labels": "username"
      }
    }
  },
  "metadata": {
    "artifact_type": "test_case",
    "type": "recorder_refined",
    "flow_name": "test56",
    "step_index": 1,
    "action": "fill"
  }
}
```

### 2. Test Script Generation Process

When generating test scripts from test56:

```python
# Step 1: Query Vector DB
results = vector_db.query("test56", top_k=50)

# Step 2: Extract locators from results
for result in results:
    payload = result['content']['payload']
    locators = payload['locators']
    
    # Step 3: Generate selector code based on priority
    if locators['playwright']:
        # Use Playwright semantic selector
        code = f"await page.{locators['playwright']}.{action}()"
    elif locators['stable']:
        # Use stable CSS selector
        code = f"await page.locator('{locators['stable']}').{action}()"
    else:
        # Fallback to XPath
        xpath = locators['xpath'] or locators['raw_xpath']
        code = f"await page.locator('{xpath}').{action}()"
```

### 3. XPath Optimization for Guidewire

The system applies Guidewire-specific optimizations:

**Original XPath (too brittle):**
```xpath
/html[1]/body[1]/form[1]/div[1]/div[2]/div[2]/div[1]/div[5]/div[2]/div[4]/div[1]/div[2]
```

**Optimized XPath (more resilient):**
```xpath
//div[@id='FNOLWizard-Next']//div[@aria-label='Next']
```

**Best Practice (Playwright semantic):**
```typescript
page.getByRole('button', { name: 'Next' })
```

## test56 Refined Flow Structure

```json
{
  "refinedVersion": "2025.10",
  "flow_name": "test56",
  "flow_id": "test56",
  "original_url": "https://cc-dev-gwcpdev.cognizant.zeta1-andromeda.guidewire.net/...",
  "steps": [
    {
      "step": 1,
      "action": "Fill",
      "navigation": "Enter username",
      "data": "username: <value>",
      "expected": "Field captures the entered data.",
      "locators": { /* Multiple selector strategies */ }
    },
    {
      "step": 2,
      "action": "Fill",
      "navigation": "Enter password",
      "data": "password: ***redacted***",
      "expected": "Field captures the entered data.",
      "locators": { /* Multiple selector strategies */ }
    },
    {
      "step": 3,
      "action": "Click",
      "navigation": "Click the Log In button",
      "data": "",
      "expected": "Element responds as expected.",
      "locators": { /* Multiple selector strategies */ }
    }
    // ... more steps
  ],
  "elements": [
    {
      "tag": "input",
      "label": "username",
      "role": "textbox",
      "xpath": "/html[1]/body[1]/form[1]//input[@name='Login-LoginScreen-LoginDV-username']",
      "css": "[name='Login-LoginScreen-LoginDV-username']"
    }
    // ... more elements
  ]
}
```

## XPath Generation Rules

### Rule 1: Prefer Semantic Selectors
```typescript
// ✅ GOOD - Resilient to UI changes
await page.getByRole('button', { name: 'Search' }).click();

// ❌ AVOID - Brittle, breaks with layout changes
await page.locator('/html[1]/body[1]/form[1]/div[1]/div[2]/div[2]/div[2]/div[1]/div[5]/div[1]/div[1]/table[1]/tbody[1]/tr[1]/td[1]/div[1]/div[1]/div[1]/div[1]/div[11]/div[2]/div[1]/div[1]/input[1]').click();
```

### Rule 2: Use Guidewire IDs When Available
```typescript
// ✅ GOOD - Guidewire IDs are stable
await page.locator('#FNOLWizard-Next').click();

// ✅ GOOD - Guidewire name attributes
await page.locator('[name="FNOLWizard-FullWizardStepSet-FNOLWizard_ServicesScreen-ttlBar"]');
```

### Rule 3: Optimize XPath for Readability
```typescript
// ❌ AVOID - Absolute XPath (brittle)
await page.locator('/html[1]/body[1]/form[1]/div[1]/div[2]/div[2]/div[1]/div[5]/div[2]/div[4]/div[1]/div[2]');

// ✅ GOOD - Relative XPath with attributes
await page.locator('//div[@id="FNOLWizard-Next"]//div[@aria-label="Next"]');

// ✅ BETTER - Playwright semantic
await page.getByRole('button', { name: 'Next' });
```

## Test Script Generation from test56

### Input: User Request
```
"Generate test script for test56 claim creation flow"
```

### Process:

#### Step 1: Vector DB Query
```python
# Query for test56 refined steps
results = vector_db.query(
    query="test56",
    where={"type": "recorder_refined", "flow_slug": "test56"}
)
```

#### Step 2: Extract Locators
```python
steps = []
for result in results:
    payload = result['content']['payload']
    steps.append({
        'action': payload['action'],
        'navigation': payload['navigation'],
        'locators': payload['locators'],
        'data': payload['data']
    })
```

#### Step 3: Generate Playwright Code
```typescript
import { test, expect } from '@playwright/test';

test('test56 - Claim Creation Flow', async ({ page }) => {
  // Step 1: Navigate to ClaimCenter
  await page.goto('https://cc-dev-gwcpdev.cognizant.zeta1-andromeda.guidewire.net/ClaimCenter.do');
  
  // Step 2: Enter username
  await page.locator('[name="Login-LoginScreen-LoginDV-username"]').fill('superuser');
  
  // Step 3: Enter password
  await page.locator('[name="Login-LoginScreen-LoginDV-password"]').fill('gw');
  
  // Step 4: Click Log In
  await page.getByRole('button', { name: 'Log In' }).click();
  
  // Step 5: Expand Claims menu
  await page.locator('#TabBar-ClaimTab .gw-icon--expand').click();
  
  // Step 6: Click New Claim
  await page.getByLabel('New Claim').click();
  
  // Step 7: Enter date
  await page.getByRole('textbox', { name: 'date input' }).fill('04/15/2024');
  
  // Step 8: Click Search
  await page.getByRole('button', { name: 'Search' }).click();
  
  // Step 9: Select policy
  await page.getByText('Select').click();
  
  // Step 10: Click Next
  await page.getByRole('button', { name: 'Next' }).click();
  
  // Step 11: Select Reported By
  await page.locator('[name*="ReportedBy_Name"]').selectOption('Person:13437');
  
  // Step 12: Click Next
  await page.getByRole('button', { name: 'Next' }).click();
  
  // Step 13: Click Next (Services)
  await page.getByRole('button', { name: 'Next' }).click();
  
  // Step 14: Click Finish
  await page.getByRole('button', { name: 'Finish' }).click();
  
  // Assertion
  await expect(page.locator('#gw-center-panel')).toBeVisible();
});
```

## XPath Storage in Vector DB

### Metadata Fields
```python
{
  "artifact_type": "test_case",
  "type": "recorder_refined",
  "record_kind": "step",  # or "element"
  "flow_name": "test56",
  "flow_slug": "test56",
  "flow_hash": "a1b2c3d4e5f6",
  "step_index": 1,
  "action": "fill",
  "navigation": "Enter username",
  "data": "username: <value>",
  "expected": "Field captures the entered data."
}
```

### Content Payload
```python
{
  "summary": "test56 | Step 1: Fill\nNavigation: Enter username\nData: username: <value>",
  "payload": {
    "flow": "test56",
    "step_index": 1,
    "action": "fill",
    "navigation": "Enter username",
    "locators": {
      "playwright": "",
      "stable": "[name='Login-LoginScreen-LoginDV-username']",
      "xpath": "/html[1]/body[1]/form[1]//input[1]",
      "css": "[name='Login-LoginScreen-LoginDV-username']",
      "xpath_candidates": [
        "/html[1]/body[1]/form[1]/div[1]/div[2]/div[2]/div[2]/div[1]/div[4]/div[4]/div[1]/div[2]/div[1]/div[1]/div[1]/div[2]/div[1]/div[1]/input[1]"
      ],
      "raw_xpath": "/html[1]/body[1]/form[1]/div[1]/div[2]/div[2]/div[2]/div[1]/div[4]/div[4]/div[1]/div[2]/div[1]/div[1]/div[1]/div[2]/div[1]/div[1]/input[1]",
      "role": "textbox",
      "labels": "username",
      "title": "",
      "name": "username"
    }
  }
}
```

## Selector Healing Strategy

When a selector fails during test execution, the system tries alternatives:

```typescript
async function robustClick(page, locators) {
  const strategies = [
    () => page.locator(locators.playwright),
    () => page.locator(locators.stable),
    () => page.locator(locators.css),
    () => page.locator(locators.xpath)
  ];
  
  for (const strategy of strategies) {
    try {
      await strategy().click({ timeout: 5000 });
      return;
    } catch (e) {
      continue;
    }
  }
  throw new Error('All selector strategies failed');
}
```

## Benefits of Multi-Selector Approach

### 1. Resilience
- If Playwright semantic selector fails → try CSS
- If CSS fails → try XPath
- Multiple fallback options

### 2. Maintainability
- Semantic selectors (getByRole) survive UI refactoring
- CSS with IDs stable for Guidewire apps
- XPath as last resort

### 3. Readability
- Playwright selectors are human-readable
- Easy to understand test intent
- Self-documenting code

### 4. Performance
- Semantic selectors are fast
- CSS selectors are optimized
- XPath only when needed

## Summary

For **test56**, the refinement process:

1. ✅ Removed ~25 duplicate input actions
2. ✅ Filtered ~15 authentication steps
3. ✅ Generated ~10 unique refined steps
4. ✅ Stored in `app/generated_flows/test56-test56.refined.json`
5. ✅ Ingested into Vector DB with multiple selector strategies
6. ✅ Each step has: Playwright, CSS, XPath, role, and label metadata

When generating test scripts, the system:
- Prioritizes Playwright semantic selectors
- Falls back to CSS with Guidewire IDs
- Uses XPath only as last resort
- Maintains sequence and data flow
- Enables robust, maintainable test automation
