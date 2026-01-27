"""Test the improved refinement with the ggggg recording"""
import json
from pathlib import Path
from app.recorder_auto_ingest import build_refined_flow_from_metadata

# Load the metadata
metadata_path = Path("recordings/ggggg/metadata.json")
with open(metadata_path, 'r', encoding='utf-8') as f:
    metadata = json.load(f)

print(f"Original actions: {len(metadata.get('actions', []))}")

# Set original URL to filter auth steps
metadata['options'] = {'url': 'https://onecognizant.cognizant.com/welcome'}

# Build refined flow
try:
    refined = build_refined_flow_from_metadata(metadata, flow_name="Test Flow")
    
    print(f"\nRefined steps: {len(refined.get('steps', []))}")
    print(f"\nSteps:")
    for step in refined.get('steps', []):
        print(f"  {step['step']}. {step['action']}: {step['navigation']}")
    
    # Save for inspection
    output_path = Path("test_refined_output.json")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(refined, f, indent=2, ensure_ascii=False)
    
    print(f"\nSaved to: {output_path}")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
