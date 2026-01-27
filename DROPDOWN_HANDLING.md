# Dropdown/Autocomplete Handling in Generated Scripts

## Problem

When recording user interactions with autocomplete/searchable dropdown fields, the recorder captures:
1. **Step N**: User types "Allied Manufacturing" into Supplier field
2. **Step N+1**: User clicks on specific dropdown option "Allied Manufacturing 10001  423424234  CORPORATION"

The generated script hardcodes Step N+1 to always click that exact option, which breaks when test data changes.

## Example Issue

```typescript
// Step 15 - Enter Supplier (CORRECT - uses test data)
await invoice12page.applyData(dataRow, ["Supplier"]);

// Step 16 - Click hardcoded option (WRONG - ignores test data)
await invoice12page.alliedManufacturing10001423424234Corporation.click();
```

**Problem**: If test data has `Supplier = "ABC Corp"`, Step 15 fills "ABC Corp" but Step 16 still clicks "Allied Manufacturing", causing test failure.

## Solution Patterns

### Pattern 1: Text-Based Selection (Recommended)
Replace hardcoded dropdown option clicks with dynamic text-based selectors:

```typescript
// Step 15 - Enter Supplier
await supplierField.fill(getDataValue('Supplier', 'Allied Manufacturing'));

// Step 16 - Click matching dropdown option dynamically
const supplierValue = getDataValue('Supplier', 'Allied Manufacturing');
await page.getByText(supplierValue).first().click();
// OR await page.locator(`text=${supplierValue}`).first().click();
```

### Pattern 2: Wait for Dropdown + Select
For dropdowns that appear after typing:

```typescript
// Step 15 - Enter Supplier
await supplierField.fill(getDataValue('Supplier', 'Allied Manufacturing'));

// Step 16 - Wait for dropdown and click matching option
const supplierValue = getDataValue('Supplier', 'Allied Manufacturing');
await page.waitForSelector('[role="listbox"]'); // Wait for dropdown to appear
await page.locator(`[role="option"]:has-text("${supplierValue}")`).first().click();
```

### Pattern 3: Partial Text Match
For dropdown options with additional text (e.g., IDs, codes):

```typescript
// If Supplier = "Allied Manufacturing" but option is "Allied Manufacturing 10001"
const supplierValue = getDataValue('Supplier', 'Allied Manufacturing');
await page.locator(`[role="option"]`).filter({ hasText: supplierValue }).first().click();
```

## Implementation in Page Objects

### Before (Hardcoded)
```typescript
// Locators
alliedManufacturing10001423424234Corporation: Locator;

// Constructor
this.alliedManufacturing10001423424234Corporation = page.locator(locators.alliedManufacturing10001423424234Corporation);

// Test
await invoice12page.alliedManufacturing10001423424234Corporation.click();
```

### After (Dynamic)
```typescript
// No hardcoded dropdown option locator needed

// Helper method in page object
async selectDropdownOption(fieldName: string, value: string): Promise<void> {
  // Wait for dropdown to appear
  await this.page.waitForSelector('[role="listbox"], [role="menu"]', { timeout: 5000 });
  
  // Click option matching value (case-insensitive partial match)
  await this.page.locator('[role="option"], [role="menuitem"]')
    .filter({ hasText: new RegExp(value, 'i') })
    .first()
    .click();
}

// Test
await invoice12page.applyData(dataRow, ["Supplier"]);
const supplierValue = getDataValue("Supplier", "Allied Manufacturing");
await invoice12page.selectDropdownOption("Supplier", supplierValue);
```

## Detection Heuristics

The LLM should detect dropdown patterns when:
1. Step N has action "Enter/Fill/Type" into a field
2. Step N+1 has action "Click" on an element whose text contains the Step N data value
3. Step N+1's locator contains identifiers suggesting it's a dropdown option (e.g., `::su0`, `option`, `menuitem`)

## Test Data Integration

Ensure `getDataValue()` or equivalent is called to retrieve the dynamic value:

```typescript
// In test spec
const supplierValue = getDataValue("Supplier", "Allied Manufacturing"); // Reads from Excel

// Or using applyData pattern
await invoice12page.applyData(dataRow, ["Supplier"]); // Fills field
await invoice12page.selectSupplierOption(getDataValue("Supplier", "Allied Manufacturing")); // Clicks option
```

## Benefits

1. ✅ **Data-driven**: Tests work with any supplier value in test data
2. ✅ **Maintainable**: No hardcoded business data in selectors
3. ✅ **Resilient**: Handles dropdown UI changes better than XPath to specific options
4. ✅ **Reusable**: `selectDropdownOption()` helper works across multiple fields

## Script Generation Updates

The prompt in `agentic_script_agent.py` now includes instructions to:
1. Detect autocomplete/dropdown fill + select patterns
2. Generate dynamic text-based selectors for dropdown options
3. Use `getDataValue()` or equivalent for dropdown selections
4. Avoid hardcoding specific dropdown option locators in the Page Object

## Testing

To verify this works:
1. Record a flow with autocomplete dropdown (e.g., Supplier selection)
2. Generate script via agentic flow
3. Check generated test for dynamic dropdown selection pattern
4. Run with different test data values to confirm it adapts

## Future Enhancements

- Auto-detect dropdown patterns during refinement
- Add metadata to refined JSON marking dropdown steps
- Generate specialized `selectFromDropdown()` helpers per field
- Support multi-select dropdowns
- Handle dropdown keyboard navigation (arrow keys + Enter)
