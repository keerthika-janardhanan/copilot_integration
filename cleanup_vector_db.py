"""
Cleanup script to remove old/duplicate flows from vector DB.
This fixes the issue where deletion was failing due to ChromaDB multi-field filter bug.
"""
from app.vector_db import VectorDBClient
import os

def cleanup_all_flows():
    """Delete all recorder_refined flows from vector DB."""
    vdb = VectorDBClient(path=os.getenv("VECTOR_DB_PATH", "./vector_store"))
    
    # Get all flows
    all_refined = vdb.list_where(where={"source": "recorder_refined"}, limit=2000)
    print(f"Found {len(all_refined)} recorder_refined documents")
    
    # Group by flow_slug
    flows = {}
    for doc in all_refined:
        flow_slug = doc['metadata'].get('flow_slug', 'unknown')
        if flow_slug not in flows:
            flows[flow_slug] = []
        flows[flow_slug].append(doc)
    
    print(f"\nFlows to delete:")
    for flow_slug, docs in sorted(flows.items()):
        print(f"  {flow_slug}: {len(docs)} documents")
    
    # Delete each flow using correct $and syntax
    total_deleted = 0
    for flow_slug in flows.keys():
        try:
            # Use $and operator for multi-field filter
            vdb.collection.delete(where={"$and": [{"flow_slug": flow_slug}, {"type": "recorder_refined"}]})
            deleted_count = len(flows[flow_slug])
            total_deleted += deleted_count
            print(f"✓ Deleted {flow_slug}: {deleted_count} documents")
        except Exception as e:
            print(f"✗ Failed to delete {flow_slug}: {e}")
    
    # Also clear hashstore for clean re-ingestion
    try:
        import sqlite3
        db_path = os.path.join(os.path.dirname(__file__), "app", "hashstore.db")
        if os.path.exists(db_path):
            conn = sqlite3.connect(db_path)
            c = conn.cursor()
            c.execute("DELETE FROM hashes WHERE key LIKE 'recorder_refined%'")
            conn.commit()
            conn.close()
            print(f"\n✓ Cleared hashstore entries")
    except Exception as e:
        print(f"\n✗ Failed to clear hashstore: {e}")
    
    # Verify deletion
    remaining = vdb.list_where(where={"source": "recorder_refined"}, limit=2000)
    print(f"\n{'='*60}")
    print(f"Summary:")
    print(f"  Total deleted: {total_deleted}")
    print(f"  Remaining: {len(remaining)}")
    
    if remaining:
        print(f"\nWarning: {len(remaining)} documents still remain!")
        # Show what's left
        remaining_flows = {}
        for doc in remaining:
            flow_slug = doc['metadata'].get('flow_slug', 'unknown')
            remaining_flows[flow_slug] = remaining_flows.get(flow_slug, 0) + 1
        print("Remaining flows:")
        for flow_slug, count in sorted(remaining_flows.items()):
            print(f"  {flow_slug}: {count} documents")
    else:
        print("\n✓ All recorder_refined flows successfully deleted!")

if __name__ == "__main__":
    import sys
    
    print("Vector DB Cleanup Script")
    print("="*60)
    print("This will delete ALL recorder_refined flows from the vector DB.")
    print("You will need to re-ingest your flows after this cleanup.")
    print("="*60)
    
    if len(sys.argv) > 1 and sys.argv[1] == "--yes":
        cleanup_all_flows()
    else:
        response = input("\nProceed with cleanup? (yes/no): ")
        if response.lower() in ['yes', 'y']:
            cleanup_all_flows()
        else:
            print("Cleanup cancelled.")
