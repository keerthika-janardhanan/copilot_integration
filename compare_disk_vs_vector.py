"""
Show which refined flow files exist on disk vs what's in vector DB.
Helps identify orphaned vector DB entries.
"""
from app.vector_db import VectorDBClient
import os
import json
from pathlib import Path

def analyze_flows():
    vdb = VectorDBClient(path=os.getenv("VECTOR_DB_PATH", "./vector_store"))
    
    # Get all flows from vector DB
    all_refined = vdb.list_where(where={"source": "recorder_refined"}, limit=2000)
    print(f"Vector DB: {len(all_refined)} recorder_refined documents")
    
    db_flows = {}
    for doc in all_refined:
        flow_slug = doc['metadata'].get('flow_slug', 'unknown')
        db_flows[flow_slug] = db_flows.get(flow_slug, 0) + 1
    
    # Get all refined JSON files from disk
    generated_flows_dir = Path("app/generated_flows")
    disk_flows = {}
    
    if generated_flows_dir.exists():
        for json_file in generated_flows_dir.glob("*.refined.json"):
            # Extract flow_slug from filename
            # Format: <name>-<flow_slug>.refined.json
            parts = json_file.stem.replace(".refined", "").split("-")
            if len(parts) >= 2:
                flow_slug = "-".join(parts[1:])  # Handle multi-part slugs
                
                # Load and count steps
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        steps = data.get('steps', [])
                        disk_flows[flow_slug] = {
                            'file': json_file.name,
                            'steps': len(steps)
                        }
                except Exception as e:
                    disk_flows[flow_slug] = {
                        'file': json_file.name,
                        'error': str(e)
                    }
    
    # Compare
    print("\n" + "="*80)
    print("COMPARISON: Disk Files vs Vector DB")
    print("="*80)
    
    all_flow_slugs = set(db_flows.keys()) | set(disk_flows.keys())
    
    print("\n✓ Flows with matching disk files (keep these):")
    for flow_slug in sorted(all_flow_slugs):
        if flow_slug in disk_flows and flow_slug in db_flows:
            disk_info = disk_flows[flow_slug]
            db_count = db_flows[flow_slug]
            if 'error' not in disk_info:
                print(f"  {flow_slug}:")
                print(f"    Disk: {disk_info['file']} ({disk_info['steps']} steps)")
                print(f"    Vector DB: {db_count} documents")
    
    print("\n✗ Orphaned flows in Vector DB (no disk file - should delete):")
    orphaned_count = 0
    for flow_slug in sorted(all_flow_slugs):
        if flow_slug in db_flows and flow_slug not in disk_flows:
            db_count = db_flows[flow_slug]
            print(f"  {flow_slug}: {db_count} documents")
            orphaned_count += db_count
    
    print("\n⚠ Flows on disk but not in Vector DB (need ingestion):")
    for flow_slug in sorted(all_flow_slugs):
        if flow_slug in disk_flows and flow_slug not in db_flows:
            disk_info = disk_flows[flow_slug]
            if 'error' not in disk_info:
                print(f"  {flow_slug}: {disk_info['file']} ({disk_info['steps']} steps)")
    
    print("\n" + "="*80)
    print("SUMMARY:")
    print(f"  Flows on disk: {len(disk_flows)}")
    print(f"  Flows in vector DB: {len(db_flows)}")
    print(f"  Orphaned vector DB documents: {orphaned_count}")
    print("="*80)
    
    if orphaned_count > 0:
        print(f"\n💡 TIP: Run cleanup_vector_db.py to remove orphaned flows")
        print(f"   Then re-ingest your current flows from disk")

if __name__ == "__main__":
    analyze_flows()
