from app.vector_db import VectorDBClient

client = VectorDBClient()

# Test deletion with multi-field filter
print("Testing deletion with multi-field where clause...")

# First, check what invoice-creation documents exist
before = client.list_where(where={"flow_slug": "invoice-creation"}, limit=200)
print(f"Before deletion: {len(before)} invoice-creation documents")

# Try to delete with multi-field filter (this is what ingest_refined_flow.py does)
try:
    print("\nAttempting delete with multi-field where clause...")
    client.collection.delete(where={"flow_slug": "invoice-creation", "type": "recorder_refined"})
    print("Delete succeeded!")
except Exception as e:
    print(f"Delete failed with error: {e}")
    print(f"Error type: {type(e).__name__}")
    
    # Try with $and operator
    print("\nAttempting delete with $and operator...")
    try:
        client.collection.delete(where={"$and": [{"flow_slug": "invoice-creation"}, {"type": "recorder_refined"}]})
        print("Delete with $and succeeded!")
    except Exception as e2:
        print(f"Delete with $and also failed: {e2}")

# Check after deletion
after = client.list_where(where={"flow_slug": "invoice-creation"}, limit=200)
print(f"\nAfter deletion: {len(after)} invoice-creation documents")
