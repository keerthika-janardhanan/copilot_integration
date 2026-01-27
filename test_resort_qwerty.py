"""Quick test to re-refine the qwerty recording with sorted timestamps."""
import json
from pathlib import Path
from app.recorder_auto_ingest import auto_refine_and_ingest

metadata_path = Path("recordings/qwerty/metadata.json")
metadata = json.loads(metadata_path.read_text(encoding="utf-8"))

print(f"Total actions in metadata: {len(metadata.get('actions', []))}")
print(f"Original URL: {metadata.get('options', {}).get('url')}")

result = auto_refine_and_ingest("recordings/qwerty", metadata, flow_name="qwerty_sorted")

print(f"\nRefined path: {result['refined_path']}")
print(f"Filtered auth steps: {result.get('filtered_auth_steps', 0)}")
print(f"Ingested: {result.get('ingested', False)}")

# Show first few steps
refined_path = Path(result['refined_path'])
refined_data = json.loads(refined_path.read_text(encoding="utf-8"))
steps = refined_data.get("steps", [])
print(f"\nTotal steps in refined flow: {len(steps)}")
print("\nFirst 5 steps:")
for step in steps[:5]:
    print(f"  {step['step']}. {step['action']}: {step['navigation'][:60]}...")
