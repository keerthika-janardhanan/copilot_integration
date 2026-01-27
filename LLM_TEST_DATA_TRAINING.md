# Test Data Mapping Reference - Explicit LLM Training

## Your Actual Test Data Structure

```
┌───────────┬──────────────────────────────┬──────────────────┬────────────┐
│ Invoice ID│         Supplier             │     Number       │   Amount   │
├───────────┼──────────────────────────────┼──────────────────┼────────────┤
│   9998    │ PrimeSource Distributors     │ CM-SHEZ2233198   │   100.00   │
│   9999    │ EverBright Traders           │ CM-SHEZ2233199   │   100.00   │
│   10000   │ Nova Industrial Solutions    │ CM-SHEZ2233200   │   100.00   │
│   10001   │ TEST_Sup_001                 │ CM-SHEZ2233201   │   100.00   │
│   10002   │ TEST_Sup_002                 │ CM-SHEZ2233202   │   100.00   │
│   10003   │ TEST_Sup_003                 │ CM-SHEZ2233203   │   100.00   │
│   10004   │ TEST_Sup_004                 │ CM-SHEZ2233204   │   100.00   │
│   10005   │ TEST_Sup_005                 │ CM-SHEZ2233205   │   100.00   │
│   10006   │ TEST_Sup_006                 │ CM-SHEZ2233206   │   100.00   │
│   10007   │ TEST_Sup_007                 │ CM-SHEZ2233207   │   100.00   │
└───────────┴──────────────────────────────┴──────────────────┴────────────┘
```

## How LLM Should Generate Code

### ❌ WRONG: What LLM Currently Generates

```typescript
// Step 20: Hardcoded supplier name
await payablespage.supplier.fill("Allied Manufacturing");

// Step 21: Hardcoded dropdown option locator
await payablespage.alliedManufacturing10001423424234Corporation.click();

// Step 23: Hardcoded invoice number
await payablespage.number.fill("INV123");

// Step 25: Hardcoded amount
await payablespage.amount.fill("100.00");
```

**Problem**: This only works with "Allied Manufacturing". When test data has "TEST_Sup_001", it fails.

---

### ✅ CORRECT: What LLM Must Generate

```typescript
// Step 19: Click to focus Supplier field
await namedStep("Step 19 - Click the Supplier drop-down", page, testinfo, async () => {
  await payablespage.supplier.click();
  const screenshot = await page.screenshot();
  attachScreenshot("Step 19 - Click the Supplier drop-down", testinfo, screenshot);
});

// Step 20: Fill Supplier from test data (Excel column "Supplier")
await namedStep("Step 20 - Enter Supplier", page, testinfo, async () => {
  await payablespage.applyData(dataRow, ["Supplier"]);
  // This will type: "TEST_Sup_001" (from Invoice ID 10001)
  // Or: "PrimeSource Distributors" (from Invoice ID 9998)
  // Or: "Nova Industrial Solutions" (from Invoice ID 10000)
  // Depends on which row is selected in testmanager.xlsx
  const screenshot = await page.screenshot();
  attachScreenshot("Step 20 - Enter Supplier", testinfo, screenshot);
});

// Step 21: Click dropdown option matching the typed supplier
await namedStep("Step 21 - Select Supplier option", page, testinfo, async () => {
  const supplierValue = getDataValue("Supplier", "Allied Manufacturing");
  // supplierValue now contains: "TEST_Sup_001" (if that's the test data row)
  
  // Wait for dropdown to appear and click matching option
  await page.locator('[role="option"]')
    .filter({ hasText: supplierValue })
    .first()
    .click();
  // Or simpler: await page.getByText(supplierValue).first().click();
  
  const screenshot = await page.screenshot();
  attachScreenshot("Step 21 - Select Supplier option", testinfo, screenshot);
});

// Step 22: Click Number field
await namedStep("Step 22 - Click the Number field", page, testinfo, async () => {
  await payablespage.number.click();
  const screenshot = await page.screenshot();
  attachScreenshot("Step 22 - Click the Number field", testinfo, screenshot);
});

// Step 23: Fill Number from test data (Excel column "Number")
await namedStep("Step 23 - Enter Number", page, testinfo, async () => {
  await payablespage.applyData(dataRow, ["Number"]);
  // This will type: "CM-SHEZ2233201" (from Invoice ID 10001)
  // Or: "CM-SHEZ2233198" (from Invoice ID 9998)
  const screenshot = await page.screenshot();
  attachScreenshot("Step 23 - Enter Number", testinfo, screenshot);
});

// Step 24: Click Amount field
await namedStep("Step 24 - Click the Amount field", page, testinfo, async () => {
  await payablespage.amount.click();
  const screenshot = await page.screenshot();
  attachScreenshot("Step 24 - Click the Amount field", testinfo, screenshot);
});

// Step 25: Fill Amount from test data (Excel column "Amount")
await namedStep("Step 25 - Enter Amount", page, testinfo, async () => {
  await payablespage.applyData(dataRow, ["Amount"]);
  // This will type: "100.00" (all rows have same amount)
  const screenshot = await page.screenshot();
  attachScreenshot("Step 25 - Enter Amount", testinfo, screenshot);
});

// Step 29: Click second Amount field (line item amount)
await namedStep("Step 29 - Click the Amount field", page, testinfo, async () => {
  await payablespage.amount2.click();
  const screenshot = await page.screenshot();
  attachScreenshot("Step 29 - Click the Amount field", testinfo, screenshot);
});

// Step 30: Fill line item amount (REUSE same "Amount" column)
await namedStep("Step 30 - Enter Amount", page, testinfo, async () => {
  await payablespage.applyData(dataRow, ["Amount"]);
  // This will type: "100.00" again (same value from Excel)
  // Page Object knows to use amount2 locator this time
  const screenshot = await page.screenshot();
  attachScreenshot("Step 30 - Enter Amount", testinfo, screenshot);
});
```

---

## Data Flow for Invoice ID 10001

```
testmanager.xlsx:
  TestCaseID: "payables"
  ReferenceID: "10001"
  DatasheetName: "PayablesData.xlsx"
                    ↓
PayablesData.xlsx (load row where Invoice ID = 10001):
  Invoice ID: 10001
  Supplier: "TEST_Sup_001"
  Number: "CM-SHEZ2233201"
  Amount: 100.00
                    ↓
dataRow = {
  "Invoice ID": 10001,
  "Supplier": "TEST_Sup_001",
  "Number": "CM-SHEZ2233201",
  "Amount": 100.00
}
                    ↓
Step 20: applyData(dataRow, ["Supplier"])
  → payablespage.setSupplier("TEST_Sup_001")
  → Types "TEST_Sup_001" into Supplier field
                    ↓
Step 21: getDataValue("Supplier", "Allied Manufacturing")
  → Looks up dataRow["Supplier"] → "TEST_Sup_001"
  → page.getByText("TEST_Sup_001").click()
  → Clicks dropdown option containing "TEST_Sup_001"
                    ↓
Step 23: applyData(dataRow, ["Number"])
  → payablespage.setNumber("CM-SHEZ2233201")
  → Types "CM-SHEZ2233201" into Number field
                    ↓
Step 25: applyData(dataRow, ["Amount"])
  → payablespage.setAmount("100.00")
  → Types "100.00" into Amount field
                    ↓
Step 30: applyData(dataRow, ["Amount"])
  → payablespage.setAmount2("100.00")  (reuses same Amount value)
  → Types "100.00" into second Amount field
```

---

## How applyData() Works in Page Object

```typescript
class PayablesPage {
  supplier: Locator;
  number: Locator;
  amount: Locator;
  amount2: Locator;

  // Individual setter methods
  async setSupplier(value: unknown): Promise<void> {
    await this.supplier.fill(`${value}`);
  }

  async setNumber(value: unknown): Promise<void> {
    await this.number.fill(`${value}`);
  }

  async setAmount(value: unknown): Promise<void> {
    await this.amount.fill(`${value}`);
  }

  async setAmount2(value: unknown): Promise<void> {
    await this.amount2.fill(`${value}`);
  }

  // Main applyData method
  async applyData(
    formData: Record<string, any>,
    keys?: string[]
  ): Promise<void> {
    const fallbackValues = {
      "Supplier": "",
      "Number": "",
      "Amount": ""
    };

    // If keys = ["Supplier"], only handle Supplier
    const shouldHandle = (key: string) => {
      if (!keys) return true;
      return keys.some(k => 
        k.replace(/[^a-z0-9]/gi, '').toLowerCase() === 
        key.replace(/[^a-z0-9]/gi, '').toLowerCase()
      );
    };

    if (shouldHandle("Supplier")) {
      const value = this.resolveDataValue(
        formData, 
        "Supplier", 
        fallbackValues["Supplier"]
      );
      await this.setSupplier(value);
    }

    if (shouldHandle("Number")) {
      const value = this.resolveDataValue(
        formData, 
        "Number", 
        fallbackValues["Number"]
      );
      await this.setNumber(value);
    }

    if (shouldHandle("Amount")) {
      const value = this.resolveDataValue(
        formData, 
        "Amount", 
        fallbackValues["Amount"]
      );
      // First call: fills amount field
      await this.setAmount(value);
    }
  }

  // Helper: Find value in dataRow (case-insensitive)
  private resolveDataValue(
    formData: Record<string, any>,
    key: string,
    fallback: string = ''
  ): string {
    const target = key.replace(/[^a-z0-9]/gi, '').toLowerCase();
    // "Supplier" → "supplier"
    
    for (const dataKey of Object.keys(formData)) {
      if (dataKey.replace(/[^a-z0-9]/gi, '').toLowerCase() === target) {
        const value = formData[dataKey];
        if (value !== null && value !== undefined && `${value}`.trim() !== '') {
          return `${value}`;
        }
      }
    }
    return fallback;
  }
}
```

---

## LLM Code Generation Rules

### Rule 1: Never Hardcode Business Data
```typescript
❌ await payablespage.supplier.fill("TEST_Sup_001");
✅ await payablespage.applyData(dataRow, ["Supplier"]);
```

### Rule 2: Use applyData for ALL Input Fields
```typescript
// Recorded data shows: "Enter TEST_Sup_001"
// Generate:
await payablespage.applyData(dataRow, ["Supplier"]);

// Recorded data shows: "Enter CM-SHEZ2233201"
// Generate:
await payablespage.applyData(dataRow, ["Number"]);

// Recorded data shows: "Enter 100.00"
// Generate:
await payablespage.applyData(dataRow, ["Amount"]);
```

### Rule 3: Dynamic Dropdown Selections
```typescript
// When recording shows: "Enter Supplier" → "Click Allied Manufacturing 10001"
// Generate TWO steps:

// Step 1: Fill the field
await payablespage.applyData(dataRow, ["Supplier"]);

// Step 2: Click matching dropdown option (NOT hardcoded locator)
const supplierValue = getDataValue("Supplier", "Allied Manufacturing");
await page.getByText(supplierValue).first().click();
```

### Rule 4: Reuse Column Names for Multiple Fields
```typescript
// Amount appears twice in the flow (header and line item)
// BOTH use the same Excel column "Amount"

// Step 25: Header amount
await payablespage.applyData(dataRow, ["Amount"]);

// Step 30: Line item amount (same data)
await payablespage.applyData(dataRow, ["Amount"]);

// Page Object handles routing to amount vs amount2 automatically
```

### Rule 5: Include Data Loading Boilerplate
```typescript
// Every test spec must have:
const dataRow = readExcelData(dataPath, dataSheetTab, dataReferenceId, dataIdColumn) ?? {};

const getDataValue = (sourceKey: string, fallback: string) => {
  const normalised = sourceKey.replace(/[^a-z0-9]/gi, '').toLowerCase();
  for (const key of Object.keys(dataRow)) {
    if (key.replace(/[^a-z0-9]/gi, '').toLowerCase() === normalised) {
      const value = dataRow[key];
      if (value !== null && value !== undefined && `${value}`.trim() !== '') {
        return `${value}`;
      }
    }
  }
  return fallback;
};
```

---

## Complete Example: Invoice Creation with TEST_Sup_001

```typescript
test.describe("payables", () => {
  run("payables", async ({ page }, testinfo) => {
    // Load test data (Invoice ID 10001)
    const dataRow = readExcelData(...) ?? {};
    // Result: { "Invoice ID": 10001, "Supplier": "TEST_Sup_001", ... }

    // Step 19: Focus field
    await payablespage.supplier.click();

    // Step 20: Type "TEST_Sup_001" from Excel
    await payablespage.applyData(dataRow, ["Supplier"]);

    // Step 21: Click dropdown option "TEST_Sup_001"
    const supplierValue = getDataValue("Supplier", "Allied Manufacturing");
    await page.getByText(supplierValue).first().click();

    // Step 22: Focus field
    await payablespage.number.click();

    // Step 23: Type "CM-SHEZ2233201" from Excel
    await payablespage.applyData(dataRow, ["Number"]);

    // Step 24: Focus field
    await payablespage.amount.click();

    // Step 25: Type "100.00" from Excel
    await payablespage.applyData(dataRow, ["Amount"]);

    // Step 29: Focus second amount field
    await payablespage.amount2.click();

    // Step 30: Type "100.00" again (same Excel column)
    await payablespage.applyData(dataRow, ["Amount"]);
  });
});
```

When test manager switches to Invoice ID 9999:
- Supplier becomes "EverBright Traders"
- Number becomes "CM-SHEZ2233199"
- Amount stays "100.00"
- Test runs successfully with new data!

---

## Summary for LLM

**When you see recorded data like:**
- "Enter TEST_Sup_001"
- "Enter CM-SHEZ2233201"
- "Enter 100.00"

**Generate:**
```typescript
await payablespage.applyData(dataRow, ["Supplier"]);
await payablespage.applyData(dataRow, ["Number"]);
await payablespage.applyData(dataRow, ["Amount"]);
```

**When you see dropdown selection like:**
- "Click Allied Manufacturing 10001 423424234 CORPORATION"

**Generate:**
```typescript
const supplierValue = getDataValue("Supplier", "Allied Manufacturing");
await page.getByText(supplierValue).first().click();
```

**Never generate:**
- Hardcoded `.fill("specific value")`
- Hardcoded `.alliedManufacturing10001423424234Corporation.click()`
- Any business data embedded in code
