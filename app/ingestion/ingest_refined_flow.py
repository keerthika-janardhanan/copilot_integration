"""
Ingest a refined recorder JSON (.refined.json) into the vector DB as per-step documents.

Usage (Windows PowerShell):
  python -m app.ingest_refined_flow --file "app\\generated_flows\\<your>.refined.json" --flow-name "Create Supplier"

This will:
- Parse the refined JSON { pages, elements, steps }
- Drop noisy rows like action == 'Type' or CSS-only artifacts
- Create one Chroma document per step with stable metadata:
    artifact_type=test_case, source=recorder_refined, flow_name, flow_hash, step_index, action, page_heading, heading
- Content kept concise (~500-1000 chars) for effective retrieval
"""
from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path

try:
    from ..core.vector_db import VectorDBClient  # type: ignore
    from .ingest_utils import ingest_artifact  # type: ignore
    from ..core.hashstore import compute_hash  # type: ignore
except ImportError:
    from app.core.vector_db import VectorDBClient
    from ingest_utils import ingest_artifact
    from hashstore import compute_hash


def _slugify(text: str) -> str:
    return re.sub(r"[^a-zA-Z0-9]+", "-", (text or "").lower()).strip("-") or "scenario"


def _looks_like_css_noise(text: str) -> bool:
    if not text:
        return False
    s = str(text).strip()
    # Patterns like '#_FOpt1\:_FOr1:...' or '::content'
    if s.startswith('#') and ('\\:' in s or '::content' in s):
        return True
    # Very long token-like selectors
    if s.startswith('#') and len(s) > 40 and re.fullmatch(r"[#._a-zA-Z0-9\\:]+", s):
        return True
    return False


def _shorten(value: str, limit: int = 800) -> str:
    v = (value or "").strip()
    return v if len(v) <= limit else v[:limit] + "..."


def remove_consecutive_duplicates(actions):
    """Remove consecutive duplicate actions and filter checkbox input/change events."""
    if not actions:
        return []
    
    deduplicated = []
    i = 0
    
    while i < len(actions):
        current = actions[i]
        css = current.get('element', {}).get('selector', {}).get('css')
        html = current.get('element', {}).get('html', '')
        is_checkbox = 'type="checkbox"' in html or 'type="radio"' in html
        
        # Skip input/change actions for checkboxes
        if is_checkbox and current['action'] in ['input', 'change']:
            i += 1
            continue
        
        # Look ahead for consecutive same element and action
        j = i + 1
        while j < len(actions):
            next_action = actions[j]
            next_css = next_action.get('element', {}).get('selector', {}).get('css')
            
            if next_css == css and next_action['action'] == current['action']:
                j += 1
            else:
                break
        
        deduplicated.append(current)
        i = j
    
    # Add step numbers
    for idx, action in enumerate(deduplicated, 1):
        action['step'] = idx
    
    return deduplicated


def transform_metadata_to_refined(metadata_path: str) -> dict:
    """Transform metadata.json to refined format with full content."""
    with open(metadata_path, 'r', encoding='utf-8') as f:
        metadata = json.load(f)
    
    # Remove consecutive duplicates
    refined_actions = remove_consecutive_duplicates(metadata['actions'])
    
    # Create refined structure with actions as steps
    refined = {
        "refinedVersion": "2025.10",
        "flow_name": metadata['flowId'],
        "flow_id": metadata['flowId'],
        "generated_at": metadata['startTime'],
        "original_url": metadata['startUrl'],
        "steps": refined_actions,
        "pages": metadata.get('pages', {})
    }
    
    return refined


def ingest_refined_file(file_path: str, flow_name: str | None = None) -> dict:
    p = Path(file_path)
    
    # Check if this is a metadata.json file and transform it
    if p.name == "metadata.json":
        data = transform_metadata_to_refined(str(p))
        # Save the transformed file
        flow_id = data.get("flow_id")
        output_path = p.parent.parent / "app" / "generated_flows" / f"{flow_id}-{flow_id}.refined.full.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"Transformed metadata.json to {output_path}")
    elif not p.exists():
        raise FileNotFoundError(f"Refined JSON not found: {file_path}")
    else:
        data = json.loads(p.read_text(encoding="utf-8"))
    steps = data.get("steps") or data.get("actions") or []
    elements = data.get("elements") or []
    pages = data.get("pages") or []
    flow_name = flow_name or data.get("flow_name") or p.stem
    flow_slug = flow_name  # Use the original flow name as slug instead of slugifying
    original_url = data.get("original_url")  # Track if auth filtering was applied

    # Build a map of useful element info keyed by xpath/title/label for quick lookup
    el_index = {}
    for e in elements:
        key = (e.get("xpath") or e.get("title") or e.get("label") or "").strip()
        if key:
            el_index[key] = e

    flow_hash = compute_hash(json.dumps(steps, ensure_ascii=False))[:12]
    source_type = "recorder_refined"
    vdb = VectorDBClient(path=os.getenv("VECTOR_DB_PATH", "./vector_store"))

    try:
        # ChromaDB requires $and for multi-field filters in delete operations
        vdb.collection.delete(where={"$and": [{"flow_slug": flow_slug}, {"type": source_type}]})
    except Exception:
        pass

    # Clear hashstore entries for this flow to allow re-ingestion
    try:
        import sqlite3
        db_path = os.path.join(os.path.dirname(__file__), "hashstore.db")
        if os.path.exists(db_path):
            conn = sqlite3.connect(db_path)
            c = conn.cursor()
            c.execute("DELETE FROM hashes WHERE key LIKE ?", (f"{flow_slug}%",))
            conn.commit()
            conn.close()
    except Exception:
        pass

    added = 0
    element_added = 0
    skipped = 0
    for idx, step in enumerate(steps, start=1):
        action = str(step.get("action") or "").strip()
        navigation = str(step.get("navigation") or "").strip()
        data_val = str(step.get("data") or "").strip()
        expected = str(step.get("expected") or "").strip()

        # Filter out noisy rows: action == 'Type' and CSS-only noise navigation
        if action.lower() == "type" and (_looks_like_css_noise(navigation) or not navigation):
            skipped += 1
            continue

        loc = step.get("locators") if isinstance(step, dict) else {}
        page_heading = str((loc or {}).get("page_heading") or "").strip()
        heading = str((loc or {}).get("heading") or "").strip()
        xpath = str((loc or {}).get("raw_xpath") or (loc or {}).get("xpath") or "").strip()
        title = str((loc or {}).get("title") or "").strip()
        labels = str((loc or {}).get("labels") or "").strip()

        # Attach a small element summary if we can resolve it
        el_key = xpath or title or labels
        el_info = el_index.get(el_key, {})

        content_payload = {
            "flow": flow_name,
            "flow_slug": flow_slug,
            "flow_hash": flow_hash,
            "step_index": idx,
            "action": action,
            "navigation": navigation,
            "data": data_val,
            "expected": expected,
            "page_heading": page_heading,
            "heading": heading,
            "xpath": xpath,
            "title": title,
            "labels": labels,
            "locators": step.get("locators"),
            "element": el_info,
        }

        # Keep content concise for retrieval while storing structured payload
        content_str = _shorten(
            f"{flow_name} | Step {idx}: {action}\nNavigation: {navigation}\nData: {data_val}\nExpected: {expected}\n"
            f"Page Heading: {page_heading} | Heading: {heading}\nXPath: {xpath} | Title/Label: {title or labels}"
        )

        metadata = {
            "artifact_type": "test_case",
            "type": "recorder_refined",
            "record_kind": "step",
            "flow_name": flow_name,
            "flow_slug": flow_slug,
            "flow_hash": flow_hash,
            "step_index": idx,
            "action": action,
            "navigation": navigation[:400],
            "data": data_val[:400],
            "expected": expected[:400],
            "page_heading": page_heading,
            "heading": heading,
            "original_url": original_url or "",  # Track filtering was applied
        }

        # Stable id per flow slug + step index
        doc_id = f"{flow_slug}-s{idx:03}"
        # Use the generic helper to perform idempotent add (hashstore-backed)
        ingest_artifact(
            source_type,
            {
                "summary": content_str,
                "payload": content_payload,
            },
            metadata,
            provided_id=doc_id,
        )
        added += 1

    for element_idx, element in enumerate(elements, start=1):
        label = (element.get("label") or element.get("name") or element.get("title") or "").strip()
        if not label:
            continue
        role = str(element.get("role") or "").strip()
        tag = str(element.get("tag") or "").strip()
        locators = {}
        if role and label:
            locators = {"byRole": {"role": role, "name": label}}
        elif label:
            locators = {"byText": label}
        payload = {
            "flow": flow_name,
            "flow_slug": flow_slug,
            "flow_hash": flow_hash,
            "element_index": element_idx,
            "label": label,
            "role": role,
            "tag": tag,
            "name": element.get("name") or "",
            "title": element.get("title") or "",
            "locators": {"playwright": locators} if locators else {},
        }
        metadata = {
            "artifact_type": "test_case",
            "type": "recorder_refined",
            "record_kind": "element",
            "flow_name": flow_name,
            "flow_slug": flow_slug,
            "flow_hash": flow_hash,
            "element_index": element_idx,
            "label": label,
            "role": role,
            "tag": tag,
        }
        doc_id = f"{flow_slug}-e{element_idx:03}"
        ingest_artifact(
            source_type,
            {
                "summary": f"{flow_name} | Element {element_idx}: {label} ({role or tag})",
                "payload": payload,
            },
            metadata,
            provided_id=doc_id,
        )
        element_added += 1

    return {
        "added": added,
        "elements": element_added,
        "skipped": skipped,
        "flow_name": flow_name,
        "flow_hash": flow_hash,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Ingest refined recorder JSON into vector DB (per-step)")
    parser.add_argument("--file", required=True, help="Path to *.refined.json")
    parser.add_argument("--flow-name", default=None, help="Override flow name (optional)")
    args = parser.parse_args(argv)

    stats = ingest_refined_file(args.file, args.flow_name)
    print(json.dumps({"status": "ok", **stats}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
