"""
Delete ALL documents from vector DB (including website docs).
Complete cleanup - leaves vector DB empty.
"""
from app.vector_db import VectorDBClient
import os

def delete_everything():
    """Delete all documents from vector DB."""
    vdb = VectorDBClient(path=os.getenv("VECTOR_DB_PATH", "./vector_store"))
    
    # Get all documents
    all_docs = vdb.list_where(where={}, limit=5000)
    print(f"Found {len(all_docs)} total documents in vector DB")
    
    if len(all_docs) == 0:
        print("Vector DB is already empty!")
        return
    
    # Group by source
    sources = {}
    for doc in all_docs:
        src = doc['metadata'].get('source', 'unknown')
        sources[src] = sources.get(src, 0) + 1
    
    print("\nDocuments by source:")
    for src, count in sorted(sources.items()):
        print(f"  {src}: {count} documents")
    
    # Delete all by getting all IDs
    all_ids = [doc['id'] for doc in all_docs]
    print(f"\nDeleting all {len(all_ids)} documents...")
    
    try:
        vdb.collection.delete(ids=all_ids)
        print("✓ Successfully deleted all documents!")
    except Exception as e:
        print(f"✗ Failed to delete: {e}")
        return
    
    # Also clear hashstore completely
    try:
        import sqlite3
        db_path = os.path.join(os.path.dirname(__file__), "app", "hashstore.db")
        if os.path.exists(db_path):
            conn = sqlite3.connect(db_path)
            c = conn.cursor()
            c.execute("DELETE FROM hashes")
            conn.commit()
            conn.close()
            print("✓ Cleared all hashstore entries")
    except Exception as e:
        print(f"✗ Failed to clear hashstore: {e}")
    
    # Verify deletion
    remaining = vdb.list_where(where={}, limit=5000)
    print(f"\n{'='*60}")
    print(f"Verification:")
    print(f"  Documents remaining: {len(remaining)}")
    if len(remaining) == 0:
        print("✓ Vector DB is now completely empty!")
    else:
        print(f"⚠ Warning: {len(remaining)} documents still remain")

if __name__ == "__main__":
    import sys
    
    print("="*60)
    print("DELETE ALL DOCUMENTS FROM VECTOR DB")
    print("="*60)
    print("WARNING: This will permanently delete ALL documents including:")
    print("  - All recorder_refined flows")
    print("  - All website documentation")
    print("  - All other ingested content")
    print("="*60)
    
    if len(sys.argv) > 1 and sys.argv[1] == "--yes":
        delete_everything()
    else:
        response = input("\nAre you SURE you want to delete everything? (type YES to confirm): ")
        if response == "YES":
            delete_everything()
        else:
            print("Deletion cancelled.")
