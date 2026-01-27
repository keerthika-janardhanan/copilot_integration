from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

try:
    from .recorder_enricher import GENERATED_DIR, slugify, _describe_step  # type: ignore
except ImportError:  # pragma: no cover - allow running as script
    from recorder_enricher import GENERATED_DIR, slugify, _describe_step  # type: ignore

REFINED_VERSION = "2025.10"


def _first_non_empty(*values: Optional[Any]) -> str:
    for value in values:
        if isinstance(value, str) and value.strip():
            return value.strip()
        if isinstance(value, (int, float)):
            return str(value)
        if isinstance(value, Iterable) and not isinstance(value, (str, bytes, dict)):
            text = ", ".join(str(item) for item in value if item)
            if text.strip():
                return text.strip()
    return ""


def _normalise_playwright_selector(selector: Any, element: Dict[str, Any]) -> str:
    if isinstance(selector, str) and selector.strip():
        return selector.strip()
    if isinstance(selector, dict):
        by_role = selector.get("byRole")
        if isinstance(by_role, dict):
            role = by_role.get("role")
            name = by_role.get("name")
            if role and name:
                return f'getByRole("{role}", name="{name}")'
        elif isinstance(by_role, str) and by_role.strip():
            return by_role.strip()
        by_label = selector.get("byLabel")
        if isinstance(by_label, str) and by_label.strip():
            return by_label.strip()
        by_text = selector.get("byText")
        if isinstance(by_text, str) and by_text.strip():
            return by_text.strip()
        by_placeholder = selector.get("byPlaceholder")
        if isinstance(by_placeholder, str) and by_placeholder.strip():
            return by_placeholder.strip()
    stable = element.get("stableSelector")
    if stable:
        return str(stable)
    css_path = element.get("cssPath")
    if css_path:
        return str(css_path)
    xpath = element.get("xpath")
    if xpath:
        return str(xpath)
    return ""


def _collect_xpath_candidates(*values: Optional[str]) -> List[str]:
    seen: List[str] = []
    for raw in values:
        if not raw:
            continue
        candidate = str(raw)
        if candidate and candidate not in seen:
            seen.append(candidate)
    return seen


def _compose_locators(action: Dict[str, Any]) -> Tuple[Dict[str, Any], str]:
    selectors = action.get("selectorStrategies") or {}
    element = action.get("element") or {}

    # New format: element.selector contains css/xpath/playwright
    selector_obj = element.get("selector") or {}
    
    playwright_selector = (
        selectors.get("aria") 
        or selectors.get("playwright") 
        or selector_obj.get("playwright")  # New format
        or element.get("playwright")  # Old format
    )
    playwright_str = _normalise_playwright_selector(playwright_selector, element)
    
    # CSS: try selectorStrategies first, then element.selector, then element.cssPath
    css = selectors.get("css") or selector_obj.get("css") or element.get("cssPath") or ""
    
    # XPath: try selectorStrategies first, then element.selector, then element.xpath
    xpath = selectors.get("xpath") or selector_obj.get("xpath") or ""
    element_xpath = element.get("xpath") or ""
    labels_raw = element.get("labels")
    if isinstance(labels_raw, (list, tuple, set)):
        labels = ", ".join(str(label) for label in labels_raw if label)
    else:
        labels = str(labels_raw or "")
    heading = _first_non_empty(element.get("nearestHeading"), element.get("heading"))
    page_heading = _first_non_empty(element.get("pageHeading"), element.get("page_heading"))

    locators: Dict[str, Any] = {
        "playwright": playwright_str,
        "stable": element.get("stableSelector") or css or element_xpath or xpath or "",
        "xpath": xpath,
        "xpath_candidates": _collect_xpath_candidates(xpath, element_xpath),
        "raw_xpath": element_xpath or xpath,
        "css": css,
        "title": element.get("title") or "",
        "labels": labels,
        "role": element.get("role") or "",
        "name": _first_non_empty(element.get("name"), element.get("ariaLabel")),
        "tag": element.get("tag") or "",
        "heading": heading,
        "page_heading": page_heading,
    }

    element_label = _first_non_empty(labels, locators["name"], locators["title"], locators["tag"])
    return locators, element_label


def _is_valid_selector(selector: str, css: str = "", xpath: str = "") -> bool:
    """Check if a selector is valid and not too generic to be useful."""
    if not selector:
        return False
    
    selector_lower = selector.lower().strip()
    
    # Reject generic element selectors
    invalid_patterns = [
        "body", "html", "document", "window",
        "html > body", "body.", "html.body"
    ]
    
    for pattern in invalid_patterns:
        if selector_lower == pattern or selector_lower.startswith(pattern + " ") or selector_lower.startswith(pattern + "."):
            return False
    
    # Reject XPath that only targets html or body
    if xpath:
        xpath_lower = xpath.lower()
        if xpath_lower in ("/html[1]", "/html[1]/body[1]", "//html", "//body", "/html", "/body"):
            return False
        # Reject XPath that ends with just /body[1]
        if xpath_lower.endswith("/body[1]") and xpath_lower.count("/") <= 3:
            return False
    
    # Reject CSS that only targets body or html
    if css:
        css_lower = css.lower().strip()
        if css_lower in ("body", "html", "html > body"):
            return False
        # Reject selectors like "body.someclass" without descendants
        if css_lower.startswith("body") and ">" not in css_lower and " " not in css_lower[4:]:
            return False
    
    return True


def _convert_action(action: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    action_type = (action.get("type") or action.get("action") or "").lower()
    extra = action.get("extra") or {}
    selectors = action.get("selectorStrategies") or {}
    element = action.get("element") or {}

    mapped_action = None
    value = None

    # Handle minimal recorder format (input/change/click)
    if action_type in ("change", "input"):
        mapped_action = "fill"
        # Try extra.value first (old format), then element.value (new format)
        value = extra.get("valueMasked") or extra.get("value") or element.get("value") or ""
    elif action_type == "click":
        mapped_action = "click"
        value = ""
    elif action_type == "press":
        key = extra.get("key") or extra.get("code") or element.get("key")
        if not key:
            return None
        mapped_action = "press"
        value = str(key)
    else:
        return None

    locators, element_label = _compose_locators(action)
    
    # Handle minimal recorder selector format
    selector_obj = element.get("selector") or {}
    playwright_selectors = selector_obj.get("playwright") or {}
    
    # Only try to extract from playwright_selectors if it's a dict
    selector = None
    if isinstance(playwright_selectors, dict):
        selector = (
            playwright_selectors.get("byRole")
            or playwright_selectors.get("byLabel")
            or playwright_selectors.get("byText")
            or playwright_selectors.get("byPlaceholder")
        )
    
    # Fallback to other selector sources
    if not selector:
        selector = (
            selector_obj.get("css")
            or selector_obj.get("xpath")
            or selectors.get("aria")
            or selectors.get("playwright")
            or locators.get("stable")
        )
    if not selector:
        selector = locators.get("css") or locators.get("raw_xpath") or ""

    # Get CSS and XPath for validation
    css_selector = selector_obj.get("css") or locators.get("css", "")
    xpath_selector = selector_obj.get("xpath") or locators.get("raw_xpath", "") or locators.get("xpath", "")
    
    # Validate selector - reject generic body/html selectors
    if not _is_valid_selector(selector, css_selector, xpath_selector):
        return None

    if not selector:
        return None

    notes = action.get("notes") or []
    description = "; ".join(n for n in notes if n)

    raw_step = {
        "action": mapped_action,
        "selector": selector,
        "value": str(value or ""),
        "url": action.get("pageUrl"),
        "description": description,
    }

    element_entry = {
        "tag": locators.get("tag", ""),
        "title": locators.get("title", ""),
        "label": element_label,
        "role": locators.get("role", ""),
        "name": locators.get("name", "") or element_label,
        "xpath": selector_obj.get("xpath") or locators.get("raw_xpath", "") or locators.get("xpath", ""),
        "css": selector_obj.get("css") or locators.get("css", ""),
        "heading": locators.get("heading", ""),
        "page_heading": locators.get("page_heading", ""),
    }

    data_label = element_label or locators.get("tag", "") or "Field"

    return {
        "raw": raw_step,
        "locators": locators,
        "element": element_entry,
        "data_label": data_label,
        "value": str(value or ""),
        "metadata": {
            "actionId": action.get("actionId"),
            "type": action_type,
        },
    }


def _filter_auth_steps(actions: List[Dict[str, Any]], original_url: Optional[str]) -> List[Dict[str, Any]]:
    """Filter out authentication steps before reaching the original URL.
    
    Strategy:
    1. Identify auth domains (microsoft, okta, etc.)
    2. Skip ALL actions until we're back on the target domain
    3. Keep only actions on the target domain
    """
    if not original_url:
        return actions
    
    from urllib.parse import urlparse
    try:
        target_parsed = urlparse(original_url)
        target_domain = target_parsed.netloc.lower()
        if not target_domain:
            return actions
    except Exception:
        return actions
    
    # Auth provider patterns
    auth_patterns = [
        'login.microsoftonline',
        'microsoftonline.com',
        'login.microsoft',
        'okta.com',
        'auth0.com',
        'oauth',
        'sso.',
        'saml',
    ]
    
    filtered = []
    for action in actions:
        page_url = action.get("pageUrl") or ""
        
        try:
            current_domain = urlparse(page_url).netloc.lower()
            
            # Skip if on auth domain
            if any(pattern in current_domain for pattern in auth_patterns):
                continue
            
            # Keep if on target domain or subdomain
            if target_domain in current_domain or current_domain in target_domain:
                filtered.append(action)
        except Exception:
            # If URL parsing fails, keep the action
            filtered.append(action)
    
    return filtered if filtered else actions


def _deduplicate_actions(actions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Remove duplicate actions by comparing CSS and XPath selectors.
    
    Simple strategy: If two consecutive actions have the same CSS or XPath, keep only the last one.
    """
    if not actions:
        return []
    
    def _get_selectors(act: Dict[str, Any]) -> Tuple[str, str]:
        """Extract CSS and XPath from action."""
        elem = act.get("element") or {}
        sel = elem.get("selector") or {}
        css = sel.get("css") or elem.get("cssPath") or ""
        xpath = sel.get("xpath") or elem.get("xpath") or ""
        return (str(css), str(xpath))
    
    deduplicated = []
    i = 0
    
    while i < len(actions):
        current = actions[i]
        current_css, current_xpath = _get_selectors(current)
        
        # Look ahead to find duplicates with same CSS or XPath
        j = i + 1
        while j < len(actions):
            next_action = actions[j]
            next_css, next_xpath = _get_selectors(next_action)
            
            # If CSS or XPath matches, it's the same element
            if (current_css and current_css == next_css) or (current_xpath and current_xpath == next_xpath):
                j += 1  # Skip to next
            else:
                break  # Different element, stop looking
        
        # Add the last action in the duplicate group
        deduplicated.append(actions[j - 1])
        i = j
    
    return deduplicated


def build_refined_flow_from_metadata(
    metadata: Dict[str, Any],
    flow_name: Optional[str] = None,
    session_dir: Optional[Path] = None,
) -> Dict[str, Any]:
    # Ensure metadata is a dict, not a string
    if isinstance(metadata, str):
        raise ValueError(f"metadata must be a dict, got string: {metadata[:100]}")
    
    actions = metadata.get("actions") or []
    if not actions:
        raise ValueError("Recorder metadata does not contain any actions.")

    # Try to read flow name from flow_name.txt file first
    flow_name_from_file = None
    if session_dir:
        flow_name_file = Path(session_dir) / "flow_name.txt"
        if flow_name_file.exists():
            try:
                flow_name_from_file = flow_name_file.read_text(encoding="utf-8").strip()
            except Exception:
                pass
    
    resolved_flow_name = flow_name or flow_name_from_file or metadata.get("flowName") or metadata.get("flow_name") or metadata.get("flowId") or metadata.get("flow_id") or "Recorder Flow"
    
    # Sort actions by timestamp to ensure chronological order
    def _get_timestamp(action: Dict[str, Any]) -> str:
        ts = action.get("timestamp") or action.get("timestampEpochMs") or action.get("receivedAt") or ""
        return str(ts)
    
    try:
        actions = sorted(actions, key=_get_timestamp)
    except Exception:
        pass
    
    # Get original URL from metadata
    # Priority: options.url > options.originalUrl > startUrl
    options = metadata.get("options") or {}
    original_url = (
        options.get("url") 
        or options.get("originalUrl") 
        or metadata.get("startUrl")
        or metadata.get("start_url")
    )
    
    # DISABLED: Authentication filtering - keep all actions including auth steps
    # Users can manually remove auth steps if needed
    # if original_url:
    #     actions = _filter_auth_steps(actions, original_url)
    
    # Remove consecutive duplicates while preserving sequence
    actions = _deduplicate_actions(actions)

    converted: List[Dict[str, Any]] = []
    for action in actions:
        entry = _convert_action(action)
        if entry:
            converted.append(entry)

    if not converted:
        # Check if there were degraded actions that couldn't be converted
        degraded_count = sum(1 for a in actions if a.get("degraded"))
        if degraded_count > 0:
            raise ValueError(
                f"No valid recorder actions found. {degraded_count} action(s) were degraded with incomplete selectors. "
                "Please perform meaningful interactions in the browser (fill forms, click buttons with proper selectors) and try again."
            )
        else:
            raise ValueError(
                "No recorder actions could be converted into refined steps. "
                "Please perform some interactions in the browser before stopping the recording."
            )

    elements_map: Dict[Tuple[str, str, str, str, str], Dict[str, Any]] = {}
    for entry in converted:
        element = entry["element"]
        key = (
            element.get("xpath", "") or "",
            element.get("css", "") or "",
            element.get("label", "") or "",
            element.get("name", "") or "",
            element.get("tag", "") or "",
        )
        if key not in elements_map:
            elements_map[key] = element

    refined_steps: List[Dict[str, Any]] = []
    previous_section = ""
    last_url = None
    for idx, entry in enumerate(converted, start=1):
        raw_step = entry["raw"]
        enriched = _describe_step(resolved_flow_name, raw_step, last_url, previous_section)
        previous_section = enriched["section"]
        if raw_step.get("action") == "goto" and raw_step.get("url"):
            last_url = raw_step.get("url")

        data_field = ""
        if raw_step.get("action") == "fill":
            value = entry["value"]
            if value:
                label = entry["data_label"]
                data_field = f"{label}: {value}" if label else value

        refined_steps.append(
            {
                "step": idx,
                "action": raw_step["action"].capitalize(),
                "navigation": enriched["navigation"],
                "data": data_field,
                "expected": enriched["expected"],
                "locators": entry["locators"],
            }
        )

    # Get original URL from metadata
    # Priority: options.url > options.originalUrl > startUrl
    options = metadata.get("options") or {}
    original_url = (
        options.get("url") 
        or options.get("originalUrl") 
        or metadata.get("startUrl")
        or metadata.get("start_url")
    )
    
    # Handle pages field - can be dict or list
    pages_data = metadata.get("pages") or {}
    if isinstance(pages_data, dict):
        pages_list = list(pages_data.values())
    else:
        pages_list = pages_data
    
    refined_flow = {
        "refinedVersion": REFINED_VERSION,
        "flow_name": resolved_flow_name,
        "flow_id": metadata.get("flowId"),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "original_url": original_url,  # Store for reference
        "pages": [
            {
                "pageId": page.get("pageId"),
                "pageUrl": page.get("pageUrl") or page.get("url"),
                "pageTitle": page.get("pageTitle") or page.get("title"),
                "mainHeading": page.get("mainHeading"),
            }
            for page in pages_list
        ],
        "elements": list(elements_map.values()),
        "steps": refined_steps,
    }
    return refined_flow


def auto_refine_and_ingest(
    session_dir: str | Path,
    metadata: Dict[str, Any],
    *,
    flow_name: Optional[str] = None,
    ingest: bool = True,
) -> Dict[str, Any]:
    session_path = Path(session_dir)
    
    # Track original action count for filtering statistics
    # Priority: options.url > options.originalUrl > startUrl
    options = metadata.get("options") or {}
    original_url = (
        options.get("url") 
        or options.get("originalUrl") 
        or metadata.get("startUrl")
        or metadata.get("start_url")
    )
    total_actions = len(metadata.get("actions") or [])
    
    refined_flow = build_refined_flow_from_metadata(metadata, flow_name=flow_name, session_dir=session_path)
    
    # Log filtering and deduplication statistics
    refined_steps = len(refined_flow.get("steps") or [])
    if original_url:
        filtered_count = total_actions - refined_steps
        if filtered_count > 0:
            print(f"[auto_refine] Filtered {filtered_count} authentication/duplicate steps")
            print(f"[auto_refine] Refined flow contains {refined_steps} unique steps")

    resolved_flow_name = refined_flow["flow_name"]
    slug = slugify(resolved_flow_name)
    session_suffix = session_path.name or metadata.get("flowId") or "session"
    output_path = GENERATED_DIR / f"{slug}-{session_suffix}.refined.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as fh:
        json.dump(refined_flow, fh, indent=2, ensure_ascii=False)

    ingest_stats: Optional[Dict[str, Any]] = None
    ingest_error: Optional[str] = None
    if ingest:
        try:
            from .ingest_refined_flow import ingest_refined_file  # type: ignore
        except ImportError:  # pragma: no cover - fallback for direct execution
            from ingest_refined_flow import ingest_refined_file  # type: ignore
        
        try:
            ingest_stats = ingest_refined_file(str(output_path), resolved_flow_name)
        except Exception as e:
            ingest_error = f"Vector DB ingestion failed: {str(e)}"
            print(f"[WARNING] {ingest_error}")

    return {
        "refined_path": str(output_path),
        "flow_name": resolved_flow_name,
        "ingested": bool(ingest_stats),
        "ingest_stats": ingest_stats,
        "ingest_error": ingest_error,
        "original_url": original_url,
        "total_actions": total_actions,
        "refined_steps": refined_steps,
        "filtered_count": total_actions - refined_steps,
    }
