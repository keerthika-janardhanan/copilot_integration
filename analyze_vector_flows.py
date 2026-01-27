from app.vector_db import VectorDBClient

client = VectorDBClient()

# Get all recorder_refined documents
refined_docs = client.list_where(where={"source": "recorder_refined"}, limit=1000)
print(f'Total recorder_refined documents: {len(refined_docs)}')

# Group by flow_slug
flows = {}
for doc in refined_docs:
    flow_slug = doc['metadata'].get('flow_slug', 'unknown')
    if flow_slug not in flows:
        flows[flow_slug] = []
    flows[flow_slug].append(doc)

print(f'\nFlows in vector DB:')
for flow_slug, docs in sorted(flows.items()):
    print(f'  {flow_slug}: {len(docs)} documents')

# Get all website documents
website_docs = client.list_where(where={"source": "website"}, limit=100)
print(f'\nTotal website documents: {len(website_docs)}')
for doc in website_docs:
    doc_id = doc.get('id', 'no-id')
    print(f'  {doc_id}')
