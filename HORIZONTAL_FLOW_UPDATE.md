# HorizontalFlowLayout.tsx Update Instructions

## Changes Needed for "Generated Test Script" Screen

### 1. Add new state variables (after line 103):
```typescript
const [editingMappingIdx, setEditingMappingIdx] = useState<number | null>(null);
const [editedColumnName, setEditedColumnName] = useState<string>('');
const [selectedCodeTab, setSelectedCodeTab] = useState<'locators' | 'pages' | 'tests'>('tests');
```

### 2. Replace the entire "AUTOMATION GENERATED SCRIPT" section (around line 3326) with the updated version that includes:
- Editable/deletable Test Data Mapping table with Actions column
- Tabbed code view (Locators, Page Objects, Test Specs)
- Individual file display with copy buttons

The table should have 5 columns:
1. Excel Column Name (editable inline)
2. Action Type (badge)
3. Occurrences (badge with count)
4. Methods Used (multiple badges)
5. Actions (Edit and Delete buttons)

The code section should have 3 tabs showing different file types separately.

Run `npm run build` in the frontend directory after making changes.
