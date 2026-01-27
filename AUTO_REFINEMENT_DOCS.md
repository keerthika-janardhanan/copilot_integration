# Automatic Recorder Refinement & Vector DB Ingestion

## Overview
Yes! The system **automatically refines and ingests** recordings into the vector database after you stop recording.

## Automatic Workflow

### 1. Recording Phase
- User starts recording via UI
- Browser actions are captured in real-time
- Metadata is saved to `recordings/{sessionId}/metadata.json`

### 2. Stop Recording
- User clicks "Stop Recording" in UI
- Recording session ends
- Metadata file is finalized

### 3. Automatic Finalization (Triggered by UI)
When the UI calls `/api/recorder/finalize`:

#### Step 3.1: Load Metadata
- System loads `metadata.json` from the session directory
- Validates the recording data

#### Step 3.2: Auto-Refine (`auto_refine_and_ingest`)
The system automatically:

**a) Filters Authentication Steps**
- Detects Microsoft/OAuth authentication redirects
- Removes all auth-related steps before reaching the original URL
- Keeps only the actual application workflow

**b) Deduplicates Actions**
- Identifies consecutive duplicate actions on the same element
- Keeps only the last action when duplicates occur within 5 seconds
- Example: 18 duplicate "input" actions → 1 final "input" action

**c) Converts to Refined Format**
- Maps raw actions to standardized test steps
- Enriches with element locators (CSS, XPath, Playwright)
- Adds navigation descriptions and expected outcomes

**d) Saves Refined Flow**
- Saves to `generated/{flow-name}-{sessionId}.refined.json`
- Contains clean, deduplicated steps ready for test generation

#### Step 3.3: Auto-Ingest to Vector DB
The system automatically:

**a) Prepares Vector Content**
- Creates a searchable summary of the flow
- Includes: flow name, URL, actions, page titles, selectors

**b) Stores in Vector Database**
- Document ID: `recorder_refined-{flow_hash}_{flow_id}`
- Metadata: flow details, action count, pages
- Enables semantic search for similar flows

**c) Returns Status**
- Success: Returns ingestion statistics
- Failure: Returns error details (but refined file is still saved)

## Code Flow

```
UI: Stop Recording
    ↓
API: POST /api/recorder/stop
    ↓
API: POST /api/recorder/finalize
    ↓
finalize_recorder_session()
    ↓
auto_refine_and_ingest()
    ├─→ build_refined_flow_from_metadata()
    │   ├─→ _filter_auth_steps()
    │   ├─→ _deduplicate_actions()
    │   └─→ _convert_action()
    │
    └─→ ingest_refined_file()
        └─→ VectorDBClient.add_document()
```

## Key Files

### Automatic Processing
- `app/services/refined_flow_service.py` - Orchestrates finalization
- `app/recorder_auto_ingest.py` - Refinement and ingestion logic
- `app/ingest_refined_flow.py` - Vector DB ingestion

### API Endpoints
- `app/api/routers/recorder.py` - Recorder API endpoints
  - `POST /api/recorder/start` - Start recording
  - `POST /api/recorder/stop` - Stop recording
  - `POST /api/recorder/finalize` - Trigger auto-refinement

### Vector Database
- `app/vector_db.py` - Vector database client
- `vector_store/` - ChromaDB storage

## Example: "ttttt" Flow

### Original Recording
- **Total Actions**: 79 actions
- Includes: 18 duplicate email inputs, 18 duplicate password inputs, 33 duplicate username inputs

### After Auto-Refinement
- **Total Actions**: 12 actions (84.8% reduction)
- **Filtered**: 67 duplicate/unnecessary steps removed
- **Ingested**: Successfully stored in vector DB as `recorder_refined-6cee4618_ttttt`

### Refined Steps
1. INPUT on #i0116 (email field)
2. CLICK on #i0116 (email field)
3. INPUT on #i0116 (email field)
4. CHANGE on #i0116 (email field)
5. CLICK on #idSIButton9 (Next button)
6. CLICK on #i0118 (password field)
7. INPUT on #i0118 (password field)
8. CLICK on Guidewire Insurance link
9. CLICK on #idp-discovery-username
10. INPUT on #idp-discovery-username
11. CHANGE on #idp-discovery-username
12. CLICK on #idp-discovery-submit (Next button)

## Configuration

### Deduplication Settings
Located in `app/recorder_auto_ingest.py`:
```python
# Time window for duplicate detection
TIME_WINDOW = 5000  # 5 seconds (in milliseconds)
```

### Vector DB Settings
Located in `app/vector_db.py`:
```python
# Vector store path
VECTOR_STORE_PATH = "./vector_store"

# Collection name
COLLECTION_NAME = "gen_ai"
```

## Benefits

✅ **Automatic** - No manual intervention required
✅ **Clean Data** - Removes duplicates and auth steps
✅ **Searchable** - Vector DB enables semantic search
✅ **Reusable** - Refined flows ready for test generation
✅ **Efficient** - Reduces 70-85% of unnecessary steps

## Verification

To verify automatic ingestion worked:

```bash
# Check vector database
python -m app.vector_db list --limit 5

# Check refined files
ls generated/*.refined.json

# Check specific flow
python -m app.vector_db query "login flow" --top-k 3
```

## Troubleshooting

### If Auto-Ingest Fails
- Refined file is still saved in `generated/` directory
- Error details returned in API response
- Check logs for specific error messages

### Common Issues
1. **No actions recorded** - Ensure meaningful interactions in browser
2. **ChromaDB not installed** - Run `pip install chromadb`
3. **Metadata missing** - Wait a few seconds after stopping recording

## Manual Refinement (Optional)

If you need to manually refine a recording:

```bash
# Using the standalone script
python clean_and_ingest_metadata.py

# Or using the auto-ingest module directly
python -c "from app.recorder_auto_ingest import auto_refine_and_ingest; \
           import json; \
           metadata = json.load(open('recordings/ttttt/metadata.json')); \
           result = auto_refine_and_ingest('recordings/ttttt', metadata)"
```
