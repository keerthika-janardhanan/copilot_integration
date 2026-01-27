"""Refine test56 recording and generate XPaths for test script generation."""
import json
import sys
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from app.recorder_auto_ingest import auto_refine_and_ingest

# Load test56 metadata
metadata_path = Path("recordings/test56/metadata.json")
with open(metadata_path, "r", encoding="utf-8") as f:
    metadata = json.load(f)

# Refine and ingest
print("Refining test56 recording...")
result = auto_refine_and_ingest(
    session_dir="recordings/test56",
    metadata=metadata,
    flow_name="test56",
    ingest=True
)

print(f"\n✅ Refinement Complete!")
print(f"   Refined file: {result['refined_path']}")
print(f"   Total actions: {result['total_actions']}")
print(f"   Refined steps: {result['refined_steps']}")
print(f"   Filtered: {result['filtered_count']}")
print(f"   Ingested: {result['ingested']}")

if result['ingest_stats']:
    print(f"\n📊 Ingestion Stats:")
    print(f"   Steps added: {result['ingest_stats']['added']}")
    print(f"   Elements added: {result['ingest_stats']['elements']}")
    print(f"   Skipped: {result['ingest_stats']['skipped']}")

# Load and display refined flow with XPaths
refined_path = Path(result['refined_path'])
with open(refined_path, "r", encoding="utf-8") as f:
    refined = json.load(f)

print(f"\n🔍 XPath Generation Examples from test56:\n")
print("=" * 80)

for step in refined['steps'][:5]:  # Show first 5 steps
    print(f"\nStep {step['step']}: {step['action']}")
    print(f"Navigation: {step['navigation']}")
    
    locators = step.get('locators', {})
    
    # Show Playwright selector (preferred)
    pw = locators.get('playwright', '')
    if pw:
        print(f"  ✓ Playwright: {pw}")
    
    # Show CSS selector
    css = locators.get('css', '')
    if css:
        print(f"  ✓ CSS: {css}")
    
    # Show XPath (raw)
    xpath = locators.get('raw_xpath', '') or locators.get('xpath', '')
    if xpath:
        print(f"  ✓ XPath: {xpath[:100]}{'...' if len(xpath) > 100 else ''}")
    
    # Show role/label for semantic locators
    role = locators.get('role', '')
    labels = locators.get('labels', '')
    if role or labels:
        print(f"  ✓ Semantic: role={role}, label={labels}")

print("\n" + "=" * 80)
print(f"\n✅ Full refined flow saved to: {refined_path}")
print(f"✅ Vector DB ingestion: {'SUCCESS' if result['ingested'] else 'FAILED'}")
