# Troubleshooting: Supplier Data Not Picked from Excel

## The Problem

Your code is correct:
```typescript
async setSupplier(value: unknown): Promise<void> {
  const finalValue = this.coerceValue(value);
  await this.supplier.fill(finalValue);
}

if (shouldHandle("Supplier")) {
  await this.setSupplier(this.resolveDataValue(formData, "Supplier", fallbackValues["Supplier"] ?? ''));
}
```

But the data isn't being filled. This means one of these is happening:

## Common Causes & Solutions

### 1. ❌ `dataRow` is Empty
**Symptom**: Nothing is typed into the Supplier field

**Cause**: Excel file not loaded or wrong row ID

**Debug**: Add this BEFORE `applyData`:
```typescript
await namedStep("Step 18 - Enter Supplier", page, testinfo, async () => {
  // DEBUG: Check what's in dataRow
  console.log('=== DEBUG dataRow ===');
  console.log('dataRow keys:', Object.keys(dataRow));
  console.log('dataRow values:', dataRow);
  console.log('Supplier column:', dataRow['Supplier']);
  console.log('=====================');
  
  await createpayablespage.applyData(dataRow, ["Supplier"]);
  const screenshot = await page.screenshot();
  attachScreenshot("Step 18 - Enter Supplier", testinfo, screenshot);
});
```

**Expected Output**:
```
=== DEBUG dataRow ===
dataRow keys: [ 'Invoice ID', 'Supplier', 'Number', 'Amount' ]
dataRow values: { 'Invoice ID': 10001, Supplier: 'TEST_Sup_001', Number: 'CM-SHEZ2233201', Amount: 100 }
Supplier column: TEST_Sup_001
=====================
```

**If Empty**:
```
=== DEBUG dataRow ===
dataRow keys: []
dataRow values: {}
Supplier column: undefined
=====================
```

**Solution**: Check testmanager.xlsx configuration

---

### 2. ❌ Column Name Mismatch
**Symptom**: `dataRow` has data but wrong column name

**Possible Excel Column Names**:
- `Supplier` ✅
- `supplier` ✅ (normalized)
- `Supplier Name` ❌ (won't match)
- `SupplierName` ❌ (won't match)
- `SUPPLIER` ✅ (normalized)

**Debug**: Check actual Excel column name
```typescript
console.log('Excel columns:', Object.keys(dataRow));
// Output: [ 'Invoice ID', 'Supplier Name', 'Number', 'Amount' ]
//                            ^^^^^^^ Problem! It's "Supplier Name" not "Supplier"
```

**Solution**: Either:
1. Rename Excel column to `Supplier` (preferred)
2. OR update Page Object to handle both:
```typescript
const fallbackValues: Record<string, string> = {
  "Supplier": "",
  "SupplierName": "",
  "Supplier Name": "",
  "Number": "",
  "Amount": "",
};

if (shouldHandle("Supplier") || shouldHandle("SupplierName") || shouldHandle("Supplier Name")) {
  let value = this.resolveDataValue(formData, "Supplier", "");
  if (!value) value = this.resolveDataValue(formData, "SupplierName", "");
  if (!value) value = this.resolveDataValue(formData, "Supplier Name", "");
  await this.setSupplier(value);
}
```

---

### 3. ❌ Wrong Reference ID
**Symptom**: Excel file loads but wrong row

**Check**: testmanager.xlsx configuration
```
TestCaseID: create_payables
ReferenceID: CreatePayables001  ← Must match Excel row
DatasheetName: CreatePayablesData.xlsx
IDName: Invoice ID  ← Must match Excel column name
```

**Excel must have**:
```
| Invoice ID | Supplier      | Number         | Amount |
| CreatePayables001 | TEST_Sup_001 | CM-SHEZ2233201 | 100.00 |
```

**Solution**: 
- Check `ReferenceID` in testmanager.xlsx matches `Invoice ID` value in data file
- Check `IDName` column exists in Excel

---

### 4. ❌ Data File Not Found
**Symptom**: Console shows warning

**Warning Message**:
```
[DATA] Test data file 'CreatePayablesData.xlsx' not found in data/
```

**Check**:
1. File exists: `framework_repos/a765e0ec2d83/data/CreatePayablesData.xlsx`
2. File name matches testmanager.xlsx exactly (case-sensitive on some systems)

**Solution**: 
- Copy your Excel file to `data/` folder
- Ensure exact name match with testmanager.xlsx

---

### 5. ❌ Data Value is Empty String
**Symptom**: Field is filled but with empty value

**Cause**: Excel cell is blank

**Debug**:
```typescript
console.log('Supplier value:', dataRow['Supplier']);
console.log('Type:', typeof dataRow['Supplier']);
console.log('Trimmed:', `${dataRow['Supplier']}`.trim());
// Output: Supplier value:    (blank spaces)
//         Type: string
//         Trimmed:           (empty)
```

**Solution**: Fill Excel cell with actual supplier name

---

## Complete Debug Test

Add this enhanced debug step:

```typescript
await namedStep("Step 18 - Enter Supplier (DEBUG)", page, testinfo, async () => {
  console.log('\n=================================================');
  console.log('DEBUG: Supplier Data Flow');
  console.log('=================================================');
  
  // 1. Check dataRow
  console.log('1. dataRow loaded:', !!dataRow);
  console.log('   dataRow keys:', Object.keys(dataRow));
  console.log('   dataRow:', JSON.stringify(dataRow, null, 2));
  
  // 2. Check Supplier column
  console.log('\n2. Supplier column check:');
  console.log('   Direct access:', dataRow['Supplier']);
  console.log('   Type:', typeof dataRow['Supplier']);
  console.log('   Is null/undefined:', dataRow['Supplier'] === null || dataRow['Supplier'] === undefined);
  console.log('   Trimmed value:', `${dataRow['Supplier'] || ''}`.trim());
  
  // 3. Check normalization
  const normaliseKey = (value: string) => value.replace(/[^a-z0-9]/gi, '').toLowerCase();
  console.log('\n3. Key normalization:');
  console.log('   Looking for: "Supplier" →', normaliseKey("Supplier"));
  console.log('   Excel columns normalized:', Object.keys(dataRow).map(k => `${k} → ${normaliseKey(k)}`));
  
  // 4. Test resolveDataValue manually
  console.log('\n4. Manual data resolution:');
  const target = normaliseKey("Supplier");
  let found = false;
  for (const entryKey of Object.keys(dataRow)) {
    if (normaliseKey(entryKey) === target) {
      console.log(`   MATCH! Excel column "${entryKey}" matches "Supplier"`);
      console.log(`   Value: "${dataRow[entryKey]}"`);
      found = true;
      break;
    }
  }
  if (!found) {
    console.log('   NO MATCH! No Excel column matches "Supplier"');
  }
  
  console.log('\n5. Calling applyData...');
  console.log('=================================================\n');
  
  await createpayablespage.applyData(dataRow, ["Supplier"]);
  
  // 6. Check what was actually typed
  const fieldValue = await createpayablespage.supplier.inputValue();
  console.log('\n6. Result:');
  console.log('   Field value after applyData:', `"${fieldValue}"`);
  console.log('=================================================\n');
  
  const screenshot = await page.screenshot();
  attachScreenshot("Step 18 - Enter Supplier (DEBUG)", testinfo, screenshot);
});
```

---

## Quick Checklist

Run through this checklist:

- [ ] Excel file exists in `data/` folder
- [ ] Excel file name in testmanager.xlsx is correct
- [ ] Excel has column named exactly `Supplier` (or `Supplier Name`)
- [ ] testmanager.xlsx has correct `ReferenceID`
- [ ] testmanager.xlsx has correct `IDName` (matches Excel ID column)
- [ ] testmanager.xlsx has `Execute: Yes` for this test
- [ ] Excel cell has actual supplier name (not blank)
- [ ] Test is reading the correct data file

---

## Example: Working Configuration

**testmanager.xlsx:**
```
TestCaseID          | DatasheetName           | ReferenceID | IDName     | Execute
create_payables     | CreatePayablesData.xlsx | 10001       | Invoice ID | Yes
```

**data/CreatePayablesData.xlsx:**
```
Invoice ID | Supplier      | Number          | Amount
10001      | TEST_Sup_001  | CM-SHEZ2233201  | 100.00
10002      | TEST_Sup_002  | CM-SHEZ2233202  | 100.00
```

**Test execution:**
```typescript
// Loads row where Invoice ID = 10001
// dataRow = { "Invoice ID": 10001, "Supplier": "TEST_Sup_001", ... }
await createpayablespage.applyData(dataRow, ["Supplier"]);
// Types "TEST_Sup_001" into supplier field ✅
```

---

## Most Likely Issues

Based on common problems, check these first:

1. **Excel file not uploaded** - File missing from `data/` folder
2. **Wrong ReferenceID** - testmanager.xlsx has wrong ID
3. **Column name mismatch** - Excel has "Supplier Name" but code looks for "Supplier"
4. **Empty cell** - Excel cell is blank or has spaces only

Run the debug code above and share the console output to identify the exact issue!
