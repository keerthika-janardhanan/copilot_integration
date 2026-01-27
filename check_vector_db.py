from app.vector_db import VectorDBClient

client = VectorDBClient()
all_docs = client.list_where(where={}, limit=1000)
print(f'Total documents: {len(all_docs)}')

sources = {}
for doc in all_docs:
    src = doc['metadata'].get('source', 'unknown')
    sources[src] = sources.get(src, 0) + 1

print(f'\nDocuments by source:')
for src, count in sorted(sources.items()):
    print(f'  {src}: {count}')

# Show document types
types = {}
for doc in all_docs:
    doc_type = doc['metadata'].get('type', 'unknown')
    types[doc_type] = types.get(doc_type, 0) + 1

print(f'\nDocuments by type:')
for doc_type, count in sorted(types.items()):
    print(f'  {doc_type}: {count}')

# Show sample document IDs
print(f'\nSample document IDs (first 20):')
for doc in all_docs[:20]:
    doc_id = doc.get('id', 'no-id')
    src = doc['metadata'].get('source', 'unknown')
    doc_type = doc['metadata'].get('type', 'unknown')
    print(f'  {doc_id} | source={src} | type={doc_type}')
