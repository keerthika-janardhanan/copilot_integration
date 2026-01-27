import json
from pathlib import Path
from app.ingest_refined_flow import _slugify, _looks_like_css_noise

file_path = "app/generated_flows/invoice-creation-invoice_creation.refined.json"
p = Path(file_path)
data = json.loads(p.read_text(encoding="utf-8"))
steps = data.get("steps") or []
flow_name = "invoice_creation"
flow_slug = _slugify(flow_name)

print(f"Total steps in JSON: {len(steps)}")
print(f"Flow slug: {flow_slug}")

skipped = []
for idx, step in enumerate(steps, start=1):
    action = str(step.get("action") or "").strip()
    navigation = str(step.get("navigation") or "").strip()
    
    # Filter out noisy rows: action == 'Type' and CSS-only noise navigation
    if action.lower() == "type" and (_looks_like_css_noise(navigation) or not navigation):
        skipped.append(idx)
        print(f"SKIPPED step {idx}: action={action}, navigation={navigation}")

print(f"\nTotal skipped: {len(skipped)}")
print(f"Should ingest: {len(steps) - len(skipped)}")
