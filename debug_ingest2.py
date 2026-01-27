import json
import os
from pathlib import Path

# Import the functions
from app.ingest_refined_flow import _slugify, _shorten
from app.ingest_utils import ingest_artifact
from app.hashstore import compute_hash

file_path = "app/generated_flows/invoice-creation-invoice_creation.refined.json"
p = Path(file_path)
data = json.loads(p.read_text(encoding="utf-8"))
steps = data.get("steps") or []
flow_name = "invoice_creation"
flow_slug = _slugify(flow_name)
flow_hash = compute_hash(json.dumps(steps, ensure_ascii=False))[:12]
source_type = "recorder_refined"

print(f"Flow: {flow_name} ({flow_slug})")
print(f"Total steps: {len(steps)}")
print(f"Flow hash: {flow_hash}\n")

# Try ingesting first 3 steps
for idx in [1, 2, 3]:
    step = steps[idx-1]
    action = str(step.get("action") or "").strip()
    navigation = str(step.get("navigation") or "").strip()
    
    content_payload = {
        "flow": flow_name,
        "step_index": idx,
        "action": action,
        "navigation": navigation,
    }
    
    content_str = f"{flow_name} | Step {idx}: {action}\nNavigation: {navigation}"
    
    metadata = {
        "artifact_type": "test_case",
        "type": source_type,
        "record_kind": "step",
        "flow_name": flow_name,
        "flow_slug": flow_slug,
        "flow_hash": flow_hash,
        "step_index": idx,
        "action": action,
    }
    
    doc_id = f"{flow_slug}-s{idx:03}"
    
    print(f"Step {idx}: doc_id={doc_id}")
    result = ingest_artifact(
        source_type,
        {"summary": content_str, "payload": content_payload},
        metadata,
        provided_id=doc_id,
    )
    print(f"  Result: {result}\n")
