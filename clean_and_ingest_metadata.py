import json
import hashlib
from pathlib import Path
from app.vector_db import VectorDBClient

def clean_metadata(metadata_path: str):
    """Remove duplicate and unnecessary steps from metadata.json"""
    with open(metadata_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    actions = data.get('actions', [])
    cleaned_actions = []
    seen = set()
    
    for action in actions:
        # Create a unique key for each action based on action type, element, and timestamp proximity
        action_type = action.get('action')
        element_selector = json.dumps(action.get('element', {}).get('selector', {}), sort_keys=True)
        
        # For consecutive duplicate actions on same element, keep only the last one
        key = f"{action_type}:{element_selector}"
        
        # Check if this is a duplicate of the previous action
        if cleaned_actions:
            last_action = cleaned_actions[-1]
            last_key = f"{last_action.get('action')}:{json.dumps(last_action.get('element', {}).get('selector', {}), sort_keys=True)}"
            
            # If same action on same element within 5 seconds, skip (it's a duplicate)
            if key == last_key and abs(action.get('timestamp', 0) - last_action.get('timestamp', 0)) < 5000:
                # Replace the last action with current one (keep the latest)
                cleaned_actions[-1] = action
                continue
        
        cleaned_actions.append(action)
    
    data['actions'] = cleaned_actions
    data['totalActions'] = len(cleaned_actions)
    
    # Save cleaned metadata
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    return data

def ingest_to_vector_db(metadata_path: str, flow_id: str):
    """Ingest cleaned metadata into vector database"""
    with open(metadata_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    client = VectorDBClient(path="./vector_store")
    
    # Create flow hash
    flow_hash = hashlib.md5(flow_id.encode()).hexdigest()[:8]
    
    # Prepare content for vector DB
    actions = data.get('actions', [])
    
    # Create a summary of the flow
    summary = f"Flow: {flow_id}\n"
    summary += f"Start URL: {data.get('startUrl', '')}\n"
    summary += f"Total Actions: {len(actions)}\n"
    summary += f"Pages: {len(data.get('pages', {}))}\n\n"
    
    # Add action sequence
    for i, action in enumerate(actions, 1):
        action_type = action.get('action', '')
        page_title = action.get('pageTitle', '')
        element_info = action.get('element', {})
        selector = element_info.get('selector', {})
        
        summary += f"{i}. {action_type.upper()}"
        if selector.get('css'):
            summary += f" on {selector.get('css')}"
        if page_title:
            summary += f" at '{page_title}'"
        summary += "\n"
    
    # Add to vector DB
    metadata = {
        "type": "recorder_refined",
        "flow_id": flow_id,
        "flow_hash": flow_hash,
        "start_url": data.get('startUrl', ''),
        "total_actions": len(actions),
        "total_pages": len(data.get('pages', {}))
    }
    
    doc_id = f"{flow_hash}_{flow_id}"
    client.add_document(
        source="recorder_refined",
        doc_id=doc_id,
        content=summary,
        metadata=metadata
    )
    
    print(f"[OK] Ingested flow '{flow_id}' into vector DB")
    print(f"  - Document ID: recorder_refined-{doc_id}")
    print(f"  - Actions: {len(actions)}")
    print(f"  - Pages: {len(data.get('pages', {}))}")

if __name__ == "__main__":
    metadata_path = r"c:\Users\2218532\PycharmProjects\guideware_test_script_generation\recordings\ttttt\metadata.json"
    flow_id = "ttttt"
    
    print(f"Cleaning metadata for flow: {flow_id}")
    cleaned_data = clean_metadata(metadata_path)
    print(f"[OK] Cleaned metadata: {cleaned_data['totalActions']} actions (from original)")
    
    print(f"\nIngesting into vector database...")
    ingest_to_vector_db(metadata_path, flow_id)
    print("\n[OK] Done!")
