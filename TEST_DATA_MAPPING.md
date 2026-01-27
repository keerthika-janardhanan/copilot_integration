# Test Data Mapping Flow in Generated Scripts

## Complete Data Flow: Excel → Test → Page Object → UI

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. EXCEL FILE (data/Invoice12Data.xlsx)                        │
├─────────────────────────────────────────────────────────────────┤
│ Invoice12ID | Supplier              | Number  | Amount         │
│ Invoice12001| Allied Manufacturing  | INV001  | 1000          │
│ Invoice12002| ABC Corporation       | INV002  | 2500          │
└─────────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────────┐
│ 2. TEST MANAGER (testmanager.xlsx)                             │
├─────────────────────────────────────────────────────────────────┤
│ TestCaseID  | DatasheetName        | ReferenceID   | IDName    │
│ invoice-12  | Invoice12Data.xlsx   | Invoice12001  | Invoice12ID│
└─────────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────────┐
│ 3. TEST SPEC (tests/invoice-12.spec.ts) - DATA LOADING         │
├─────────────────────────────────────────────────────────────────┤
│ test.beforeAll(() => {                                          │
│   // Load test manager to find which data file to use           │
│   executionList = getTestToRun('../testmanager.xlsx');          │
│ });                                                              │
│                                                                  │
│ run("invoice-12", async ({ page }, testinfo) => {              │
│   const testCaseId = testinfo.title; // "invoice-12"           │
│                                                                  │
│   // Find row in test manager for this test case                │
│   const testRow = executionList?.find(                          │
│     row => row['TestCaseID'] === testCaseId                    │
│   ) ?? {};                                                       │
│                                                                  │
│   // Extract data file info                                     │
│   const dataSheetName = testRow?.['DatasheetName'] ||          │
│                         'Invoice12Data.xlsx';                   │
│   const dataReferenceId = testRow?.['ReferenceID'] ||          │
│                           'Invoice12001';                       │
│   const dataIdColumn = testRow?.['IDName'] ||                  │
│                        'Invoice12ID';                           │
│                                                                  │
│   // Read Excel data row                                        │
│   const dataPath = path.join(__dirname, '../data',            │
│                               dataSheetName);                   │
│   dataRow = readExcelData(                                      │
│     dataPath,           // data/Invoice12Data.xlsx            │
│     '',                 // Sheet name (first sheet if blank)   │
│     dataReferenceId,    // 'Invoice12001'                     │
│     dataIdColumn        // 'Invoice12ID'                       │
│   );                                                             │
│   // Result: dataRow = {                                        │
│   //   Invoice12ID: 'Invoice12001',                            │
│   //   Supplier: 'Allied Manufacturing',                       │
│   //   Number: 'INV001',                                       │
│   //   Amount: 1000                                            │
│   // }                                                           │
│                                                                  │
│   // Helper to get data values with fallback                   │
│   const getDataValue = (sourceKey: string, fallback: string) => {│
│     const normalised = sourceKey.replace(/[^a-z0-9]/gi, '')   │
│                                 .toLowerCase();                 │
│     for (const key of Object.keys(dataRow)) {                  │
│       if (key.replace(/[^a-z0-9]/gi, '')                      │
│              .toLowerCase() === normalised) {                  │
│         const value = dataRow[key];                            │
│         if (value !== null && value !== undefined &&          │
│             `${value}`.trim() !== '') {                        │
│           return `${value}`;                                   │
│         }                                                       │
│       }                                                          │
│     }                                                            │
│     return fallback;                                            │
│   };                                                             │
└─────────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────────┐
│ 4. TEST SPEC - STEP EXECUTION WITH DATA                        │
├─────────────────────────────────────────────────────────────────┤
│ await namedStep("Step 15 - Enter Supplier", ..., async () => { │
│   // METHOD 1: Using applyData (passes entire dataRow)         │
│   await invoice12page.applyData(dataRow, ["Supplier"]);        │
│   // This calls page object's applyData method ────────────────┐│
│ });                                                             ││
│                                                                 ││
│ // OR                                                           ││
│                                                                 ││
│ await namedStep("Step 15 - Enter Supplier", ..., async () => { ││
│   // METHOD 2: Using getDataValue (extracts single value)      ││
│   const supplierValue = getDataValue("Supplier",               ││
│                                      "Allied Manufacturing");   ││
│   await invoice12page.supplier.fill(supplierValue);            ││
│   // Direct fill with extracted value                          ││
│ });                                                             ││
└─────────────────────────────────────────────────────────────────┘│
                          ↓                                       ││
┌─────────────────────────────────────────────────────────────────┘│
│ 5. PAGE OBJECT (pages/Invoice12Page.ts) - DATA PROCESSING      │
├─────────────────────────────────────────────────────────────────┤
│ class Invoice12page {                                           │
│   supplier: Locator;  // Initialized with locator              │
│   number: Locator;                                              │
│   amount: Locator;                                              │
│                                                                  │
│   // Helper: Normalize keys (ignore spaces, case, special chars)│
│   private normaliseDataKey(value: string): string {             │
│     return value.replace(/[^a-z0-9]+/gi, '').toLowerCase();    │
│   }                                                              │
│   // 'Supplier' → 'supplier'                                    │
│   // 'Invoice_Number' → 'invoicenumber'                         │
│                                                                  │
│   // Helper: Find matching value from dataRow                   │
│   private resolveDataValue(                                     │
│     formData: Record<string, any>,  // The dataRow             │
│     key: string,                    // "Supplier"              │
│     fallback: string = ''           // Default if not found    │
│   ): string {                                                   │
│     const target = this.normaliseDataKey(key); // "supplier"   │
│     if (formData) {                                             │
│       for (const entryKey of Object.keys(formData)) {          │
│         // Check if dataRow key matches (case-insensitive)      │
│         if (this.normaliseDataKey(entryKey) === target) {      │
│           const candidate = formData[entryKey];                 │
│           if (candidate !== null && `${candidate}`.trim() !== '') {│
│             return `${candidate}`;                              │
│           }                                                      │
│         }                                                        │
│       }                                                          │
│     }                                                            │
│     return fallback;                                            │
│   }                                                              │
│   // Example: resolveDataValue(dataRow, "Supplier", "")        │
│   //   → Finds dataRow["Supplier"] → "Allied Manufacturing"    │
│                                                                  │
│   // Setter method for specific field                           │
│   async setSupplier(value: unknown): Promise<void> {            │
│     const finalValue = this.coerceValue(value);                 │
│     await this.supplier.fill(finalValue);                       │
│   }                                                              │
│                                                                  │
│   // Main data application method                               │
│   async applyData(                                              │
│     formData: Record<string, any>,  // dataRow from test       │
│     keys?: string[]                 // ["Supplier", "Number"]  │
│   ): Promise<void> {                                            │
│     // Define fallback values if data not found                 │
│     const fallbackValues = {                                    │
│       "Supplier": "",                                           │
│       "Number": "",                                             │
│       "Amount": ""                                              │
│     };                                                           │
│                                                                  │
│     // Normalize requested keys                                 │
│     const targetKeys = keys?.map(k =>                           │
│       this.normaliseDataKey(k)                                  │
│     );                                                           │
│     // ["Supplier", "Number"] → ["supplier", "number"]         │
│                                                                  │
│     // Check if should handle this key                          │
│     const shouldHandle = (key: string) => {                     │
│       if (!targetKeys) return true; // Handle all if none specified│
│       return targetKeys.includes(                               │
│         this.normaliseDataKey(key)                              │
│       );                                                         │
│     };                                                           │
│                                                                  │
│     // Fill Supplier field if requested                         │
│     if (shouldHandle("Supplier")) {                             │
│       const value = this.resolveDataValue(                      │
│         formData,           // dataRow                          │
│         "Supplier",         // Key to find                      │
│         fallbackValues["Supplier"]  // "" if not found         │
│       );                                                         │
│       await this.setSupplier(value);                            │
│       // Fills: "Allied Manufacturing"                          │
│     }                                                            │
│                                                                  │
│     // Fill Number field if requested                           │
│     if (shouldHandle("Number")) {                               │
│       const value = this.resolveDataValue(                      │
│         formData, "Number", fallbackValues["Number"]           │
│       );                                                         │
│       await this.setNumber(value);                              │
│       // Fills: "INV001"                                        │
│     }                                                            │
│                                                                  │
│     // Fill Amount field if requested                           │
│     if (shouldHandle("Amount")) {                               │
│       const value = this.resolveDataValue(                      │
│         formData, "Amount", fallbackValues["Amount"]           │
│       );                                                         │
│       await this.setAmount(value);                              │
│       // Fills: "1000"                                          │
│     }                                                            │
│   }                                                              │
│ }                                                                │
└─────────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────────┐
│ 6. BROWSER UI - ACTUAL INTERACTION                             │
├─────────────────────────────────────────────────────────────────┤
│ [Supplier Field] ← Types "Allied Manufacturing"                │
│ [Number Field]   ← Types "INV001"                              │
│ [Amount Field]   ← Types "1000"                                │
└─────────────────────────────────────────────────────────────────┘
```

## Key Mapping Features

### 1. **Flexible Key Matching**
Excel columns don't need exact case/format match:
```typescript
Excel: "Supplier" → matches → Page Object: "Supplier"
Excel: "supplier" → matches → Page Object: "Supplier"
Excel: "SUPPLIER" → matches → Page Object: "Supplier"
Excel: "Supplier_Name" → matches → Page Object: "Supplier"
```

All normalized to: `"supplier"` (lowercase, no special chars)

### 2. **Selective Field Updates**
```typescript
// Update only Supplier
await invoice12page.applyData(dataRow, ["Supplier"]);

// Update multiple fields
await invoice12page.applyData(dataRow, ["Supplier", "Number", "Amount"]);

// Update all defined fields (no filter)
await invoice12page.applyData(dataRow);
```

### 3. **Fallback Values**
```typescript
const fallbackValues = {
  "Supplier": "",      // Empty string if not found
  "Number": "",
  "Amount": ""
};
```

If Excel doesn't have a "Supplier" column or value is empty, uses fallback.

### 4. **Type Coercion**
```typescript
private coerceValue(value: unknown): string {
  if (value === undefined || value === null) return '';
  if (typeof value === 'number') return `${value}`;  // 1000 → "1000"
  if (typeof value === 'string') return value;
  return `${value ?? ''}`;
}
```

Converts all values to strings for `fill()` operations.

## Example Execution Trace

```
Test: invoice-12
├─ Load testmanager.xlsx
│  └─ Find TestCaseID='invoice-12' → DatasheetName='Invoice12Data.xlsx', ReferenceID='Invoice12001'
├─ Load Excel: data/Invoice12Data.xlsx
│  └─ Find row where Invoice12ID='Invoice12001'
│     └─ Result: { Invoice12ID: 'Invoice12001', Supplier: 'Allied Manufacturing', Number: 'INV001', Amount: 1000 }
├─ Step 15: Enter Supplier
│  ├─ Call: await invoice12page.applyData(dataRow, ["Supplier"])
│  ├─ Page Object receives: dataRow = { Supplier: 'Allied Manufacturing', ... }
│  ├─ normaliseDataKey("Supplier") → "supplier"
│  ├─ resolveDataValue(dataRow, "Supplier", "") → "Allied Manufacturing"
│  ├─ setSupplier("Allied Manufacturing")
│  └─ Browser: Types "Allied Manufacturing" into supplier field
└─ Step 18: Enter Number
   ├─ Call: await invoice12page.applyData(dataRow, ["Number"])
   ├─ resolveDataValue(dataRow, "Number", "") → "INV001"
   ├─ setNumber("INV001")
   └─ Browser: Types "INV001" into number field
```

## Current Issue with Step 16

```typescript
// Step 15 - Fills Supplier field with test data ✅
await invoice12page.applyData(dataRow, ["Supplier"]);
// Result: Types "Allied Manufacturing" (or whatever is in Excel)

// Step 16 - Clicks HARDCODED dropdown option ❌
await invoice12page.alliedManufacturing10001423424234Corporation.click();
// Problem: Always clicks "Allied Manufacturing" regardless of test data
```

### Fix Required
```typescript
// Step 16 should dynamically select based on test data
const supplierValue = getDataValue("Supplier", "Allied Manufacturing");
await page.getByText(supplierValue).first().click();
// Now clicks whatever supplier name is in the Excel file
```

## Summary

1. **Test Manager** tells which Excel file and row to use
2. **Test Spec** loads Excel data into `dataRow` object
3. **Test Spec** passes `dataRow` to page object's `applyData()` method
4. **Page Object** normalizes keys, finds matching values, fills fields
5. **Browser** receives the typed values

The mapping is **flexible** (case/format insensitive) and **selective** (can update specific fields only).
