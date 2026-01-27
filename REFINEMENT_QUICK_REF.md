# Recorder Refinement Process - Quick Reference

## What Happens After Recording

### Step 1: Recording Stops
- Metadata saved to `recordings/{session_id}/metadata.json`
- Contains all raw actions with timestamps

### Step 2: Refinement (Automatic)
**Location:** `app/recorder_auto_ingest.py`

```python
# 1. Sort by timestamp
actions = sorted(actions, key=timestamp)

# 2. Filter authentication steps
actions = _filter_auth_steps(actions, original_url)

# 3. Remove consecutive duplicates
actions = _deduplicate_actions(actions)

# 4. Convert to refined format
refined_steps = convert_actions(actions)
```

### Step 3: Save Refined Flow
**Location:** `app/generated_flows/{flow-name}-{session}.refined.json`

**Format:**
```json
{
  "flow_name": "Create Supplier",
  "steps": [
    {
      "step": 1,
      "action": "Click",
      "navigation": "Click the Next button",
      "data": "",
      "expected": "Element responds as expected.",
      "locators": { ... }
    }
  ],
  "elements": [ ... ]
}
```

### Step 4: Vector DB Ingestion (Automatic)
**Location:** `app/ingest_refined_flow.py`

- Creates one ChromaDB document per step
- Metadata includes: flow_name, step_index, action, navigation
- Enables semantic search for test generation

## Deduplication Logic

**Removes consecutive duplicates based on:**
- Action type (click, fill, press)
- Page URL
- Element xpath
- Input value

**Example:**
```
Before: [click button1, click button1, fill input1, fill input1, click button2]
After:  [click button1, fill input1, click button2]
```

## Statistics Returned

```json
{
  "refined_path": "app/generated_flows/create-supplier-test56.refined.json",
  "flow_name": "Create Supplier",
  "ingested": true,
  "total_actions": 50,
  "refined_steps": 35,
  "filtered_count": 15,
  "ingest_stats": {
    "added": 35,
    "elements": 20,
    "skipped": 0
  }
}
```

## Troubleshooting

### No steps after refinement
- Check if original URL was reached
- Verify actions have valid selectors
- Check logs for filtering statistics

### Duplicates still present
- Only consecutive duplicates are removed
- Non-consecutive duplicates may be intentional user actions
- Check if actions have different timestamps or values

### Vector DB not updated
- Check `ingest_error` in response
- Verify ChromaDB is running
- Check `VECTOR_DB_PATH` environment variable
