# Authentication Filtering - Quick Reference

## For Users

### What it does
Automatically removes Microsoft/OAuth login steps from your recordings, keeping only your application interactions.

### How to use
Just provide a URL when recording - that's it!

```powershell
# CLI
python -m app.run_playwright_recorder_v2 --url "https://yourapp.com/page"

# UI
Enter your target URL → Click Record → Complete auth → Interact with app → Stop
```

### What you'll see
```
[auto_refine] Filtered 12 authentication steps before reaching https://yourapp.com
[auto_refine] Refined flow contains 35 steps starting from the target application
```

---

## For Developers

### Key Files
- **Filter Logic**: `app/recorder_auto_ingest.py::_filter_auth_steps()`
- **Refinement**: `app/recorder_auto_ingest.py::build_refined_flow_from_metadata()`
- **Ingestion**: `app/ingest_refined_flow.py::ingest_refined_file()`
- **Tests**: `test_auth_filtering.py`

### How It Works
```python
# 1. Detect external auth domain
if 'microsoftonline' in domain or 'login.' in domain:
    saw_external_domain = True

# 2. Wait for return to target domain
if saw_external_domain and current_domain == target_domain:
    reached_original = True
    # Start including actions from here

# 3. Result: Only app steps in refined flow
```

### Data Flow
```
metadata.json (options.url) 
  → _filter_auth_steps(actions, original_url)
  → build_refined_flow_from_metadata()
  → refined.json (with original_url field)
  → Vector DB (original_url in metadata)
```

### Testing
```powershell
.\.venv\Scripts\python.exe -m pytest test_auth_filtering.py -v
```

### Configuration
None needed! Automatic based on:
- Presence of `options.url` in metadata
- Detection of external auth providers

### Supported Auth Providers
- Microsoft (login.microsoftonline.com)
- Generic OAuth (oauth, auth., sso.)
- Any external login domain

### Edge Cases
| Scenario | Behavior |
|----------|----------|
| No URL provided | Keep all steps (no filtering) |
| No auth detected | Keep all steps |
| Never reaches target | Keep all steps (fallback) |
| Same-domain auth | No filtering |

### Return Value
```python
{
    "refined_path": "app/generated_flows/...",
    "original_url": "https://...",
    "filtered_auth_steps": 12,  # How many removed
    "ingested": True,
    "ingest_stats": {...}
}
```

### Debugging
1. Check console logs for filtering statistics
2. Inspect `metadata.json` for `options.url`
3. Compare raw actions count vs refined steps count
4. Review `refined.json` for `original_url` field

### Common Issues
- **All steps filtered**: Target domain never reached → Check URL
- **Auth steps remain**: No external domain detected → Verify auth provider
- **Nothing filtered**: `options.url` not set → Pass --url or use UI

---

## Quick Examples

### Good URL (Will Filter)
```
https://fusionapp.oracle.com/supplier/create
```
**Result**: Filters Microsoft login, keeps supplier creation steps

### No Filtering Needed
```
https://localhost:3000/dashboard
```
**Result**: No external auth → Keeps all steps

### Subdomain Matching
```
URL: app.example.com
Matches: login.app.example.com, app.example.com/page
```

---

## See Also
- **User Guide**: `AUTHENTICATION_FILTERING.md`
- **Implementation**: `IMPLEMENTATION_SUMMARY.md`
- **Tests**: `test_auth_filtering.py`
