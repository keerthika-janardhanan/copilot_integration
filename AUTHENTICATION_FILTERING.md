# Authentication Step Filtering

## Overview

The recorder automatically filters out authentication steps (e.g., Microsoft login redirects) when refining and ingesting recorded flows. This ensures that the final test cases and generated flows start from your intended application URL, not from authentication pages.

## How It Works

### 1. Recording Phase
When you start a recording with a URL (e.g., via the React UI or CLI):

```powershell
python -m app.run_playwright_recorder_v2 --url "https://your-app.example.com/home" --capture-dom
```

The recorder:
- **Records ALL steps** including authentication flows (Microsoft login, redirects, etc.)
- **Stores the original URL** in `metadata.json` under `options.url`
- Continues recording until you press Ctrl+C

### 2. Refinement Phase (Automatic)
When the recording is finalized, `auto_refine_and_ingest()` automatically:

1. **Detects the original URL** from metadata options
2. **Filters actions** by comparing page URLs to the original domain
3. **Keeps only steps** that occur after reaching the original application domain
4. **Logs filtering statistics** showing how many auth steps were removed

Example output:
```
[auto_refine] Filtered 12 authentication steps before reaching https://your-app.example.com
[auto_refine] Refined flow contains 45 steps starting from the target application
```

### 3. Storage
The refined flow saved to `app/generated_flows/` includes:
- `original_url`: The URL you provided
- `steps`: Only the steps from your application (auth steps removed)
- Metadata about filtering in the result

### 4. Vector DB Ingestion
When ingested into the vector database, each step includes:
- `original_url` metadata field
- Only application-specific steps (authentication filtered out)
- Complete locator and element information

## Example Scenario

**Initial URL provided**: `https://myapp.oracle.com/supplier/create`

**What gets recorded** (all steps):
1. Navigate to myapp.oracle.com
2. Redirect to login.microsoftonline.com
3. Fill in email
4. Click Next
5. Fill in password
6. Click Sign In
7. Redirect to myapp.oracle.com/supplier/create  ← **Original URL reached**
8. Click "Create Supplier" button
9. Fill in supplier name
10. ...etc

**What gets refined** (filtered):
1. Click "Create Supplier" button  ← **Starts here**
2. Fill in supplier name
3. ...etc

Steps 1-7 (authentication) are automatically removed because they occur before reaching the original domain.

## Domain Matching Logic

The filtering uses flexible domain matching:
- `target_domain in current_domain` OR `current_domain in target_domain`
- This handles subdomains and variations
- Example: `myapp.oracle.com` matches `login.myapp.oracle.com`

## Benefits

1. **Cleaner test cases**: No authentication noise in generated tests
2. **Reusable flows**: Test cases focus on actual application workflows
3. **Better vector search**: Vector DB contains only relevant application steps
4. **Automatic handling**: No manual editing required
5. **Preserved raw data**: Original metadata.json still contains all steps for debugging

## Configuration

No configuration needed! The feature is automatic when:
- You provide a URL via `--url` (CLI) or the UI
- The recorder reaches that URL after authentication
- Refinement runs (automatically or via API)

## Fallback Behavior

If filtering fails or original URL is not provided:
- All recorded steps are kept
- No filtering occurs
- A warning is logged if no steps remain after filtering

## Files Modified

- `app/run_playwright_recorder_v2.py`: Stores original URL in metadata
- `app/recorder_auto_ingest.py`: Implements filtering logic
- `app/ingest_refined_flow.py`: Preserves original_url in vector DB
- `app/recorder_enricher.py`: Documentation updates

## Testing

To test the filtering:

1. Record a flow with authentication:
```powershell
python -m app.run_playwright_recorder_v2 --url "https://your-app.com/page" --capture-dom
```

2. Complete authentication and interact with the app
3. Stop recording (Ctrl+C)
4. Check the console output for filtering statistics
5. Verify `app/generated_flows/*.refined.json` contains only app steps

## Troubleshooting

**Q: My steps are missing after refinement**
- Check if the original URL domain matches where you ended up
- Verify the URL in metadata.json options.url
- Check console logs for filtering statistics

**Q: Authentication steps are still present**
- Ensure the original URL was provided when starting the recorder
- Check if domains actually differ (same-domain auth won't be filtered)

**Q: I want to keep authentication steps**
- Don't provide a `--url` parameter
- Or manually edit the refined JSON after generation
