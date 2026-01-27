"""Test authentication step filtering in recorder_auto_ingest."""
import pytest
from app.recorder_auto_ingest import _filter_auth_steps


def test_filter_auth_steps_no_url():
    """When no original URL is provided, all actions should be kept."""
    actions = [
        {"pageUrl": "https://login.microsoft.com", "action": "click"},
        {"pageUrl": "https://myapp.com/home", "action": "fill"},
    ]
    result = _filter_auth_steps(actions, None)
    assert len(result) == 2
    assert result == actions


def test_filter_auth_steps_removes_microsoft_auth():
    """Should remove Microsoft authentication steps before reaching original URL."""
    actions = [
        {"pageUrl": "https://myapp.oracle.com/init", "action": "navigate"},
        {"pageUrl": "https://login.microsoftonline.com", "action": "click"},
        {"pageUrl": "https://login.microsoftonline.com", "action": "fill", "extra": {"value": "user@email.com"}},
        {"pageUrl": "https://login.microsoftonline.com", "action": "click"},
        {"pageUrl": "https://login.microsoftonline.com", "action": "fill", "extra": {"value": "password"}},
        {"pageUrl": "https://login.microsoftonline.com/auth", "action": "click"},
        {"pageUrl": "https://myapp.oracle.com/supplier/create", "action": "click"},  # Original URL reached
        {"pageUrl": "https://myapp.oracle.com/supplier/create", "action": "fill"},
        {"pageUrl": "https://myapp.oracle.com/supplier/save", "action": "click"},
    ]
    
    result = _filter_auth_steps(actions, "https://myapp.oracle.com/supplier/create")
    
    # Should keep only actions from index 6 onwards (after reaching original domain)
    assert len(result) == 3
    assert all("myapp.oracle.com" in a["pageUrl"] for a in result)
    assert result[0]["action"] == "click"
    assert result[1]["action"] == "fill"
    assert result[2]["action"] == "click"


def test_filter_auth_steps_subdomain_matching():
    """Should handle subdomain variations when matching."""
    actions = [
        {"pageUrl": "https://auth.example.com", "action": "click"},
        {"pageUrl": "https://app.example.com/home", "action": "fill"},
        {"pageUrl": "https://app.example.com/next", "action": "click"},
    ]
    
    # Should match when target is app.example.com
    result = _filter_auth_steps(actions, "https://app.example.com/home")
    assert len(result) == 2
    assert "app.example.com" in result[0]["pageUrl"]


def test_filter_auth_steps_keeps_all_if_no_match():
    """Should keep all actions if original domain is never reached."""
    actions = [
        {"pageUrl": "https://login.microsoft.com", "action": "click"},
        {"pageUrl": "https://login.microsoft.com/auth", "action": "fill"},
    ]
    
    result = _filter_auth_steps(actions, "https://myapp.com/home")
    
    # Fallback: keep all actions if we never reach the original domain
    assert len(result) == 2


def test_filter_auth_steps_handles_empty_urls():
    """Should handle actions with missing or empty URLs."""
    actions = [
        {"pageUrl": "", "action": "click"},
        {"pageUrl": "https://myapp.com/home", "action": "fill"},
        {"action": "click"},  # No pageUrl field
    ]
    
    result = _filter_auth_steps(actions, "https://myapp.com/home")
    
    # Should find the matching URL and include it plus subsequent actions
    assert len(result) >= 1
    assert any("myapp.com" in (a.get("pageUrl") or "") for a in result)


def test_filter_auth_steps_oracle_fusion_scenario():
    """Test realistic Oracle Fusion authentication flow."""
    actions = [
        {"pageUrl": "https://fusionapp.oracle.com/fscmUI/faces/init", "action": "navigate"},
        {"pageUrl": "https://login.microsoftonline.com/oauth2/authorize", "action": "wait"},
        {"pageUrl": "https://login.microsoftonline.com/login", "action": "fill"},
        {"pageUrl": "https://login.microsoftonline.com/login", "action": "click"},
        {"pageUrl": "https://login.microsoftonline.com/password", "action": "fill"},
        {"pageUrl": "https://login.microsoftonline.com/password", "action": "click"},
        {"pageUrl": "https://fusionapp.oracle.com/fscmUI/faces/FscmCreateSupplier", "action": "click"},
        {"pageUrl": "https://fusionapp.oracle.com/fscmUI/faces/FscmCreateSupplier", "action": "fill"},
    ]
    
    result = _filter_auth_steps(actions, "https://fusionapp.oracle.com/fscmUI/faces/FscmCreateSupplier")
    
    # Should filter out 6 Microsoft auth steps, keeping only the 2 supplier creation steps
    assert len(result) == 2
    assert all("fusionapp.oracle.com" in a["pageUrl"] for a in result)
    assert result[0]["action"] == "click"
    assert result[1]["action"] == "fill"


def test_filter_auth_steps_cognizant_scenario():
    """Test Cognizant OneCognizant portal authentication."""
    actions = [
        {"pageUrl": "https://onecognizant.cognizant.com/Welcome", "action": "navigate"},
        {"pageUrl": "https://login.microsoftonline.com/common/oauth2/authorize", "action": "wait"},
        {"pageUrl": "https://login.microsoftonline.com/login", "action": "fill"},
        {"pageUrl": "https://login.microsoftonline.com", "action": "click"},
        {"pageUrl": "https://onecognizant.cognizant.com/Welcome", "action": "click"},  # Back to original
        {"pageUrl": "https://onecognizant.cognizant.com/Dashboard", "action": "fill"},
    ]
    
    result = _filter_auth_steps(actions, "https://onecognizant.cognizant.com/Welcome")
    
    # Should keep from when we return to onecognizant.cognizant.com
    assert len(result) == 2
    assert all("onecognizant.cognizant.com" in a["pageUrl"] for a in result)


def test_chronological_sorting():
    """Test that actions are sorted by timestamp to ensure correct sequence."""
    from app.recorder_auto_ingest import build_refined_flow_from_metadata
    
    # Actions deliberately out of order by timestamp
    metadata = {
        "actions": [
            {
                "pageUrl": "https://app.com/page",
                "action": "click",
                "type": "click",
                "timestamp": "2026-01-07T10:00:03.000000+00:00",  # Third
                "element": {"tag": "button", "xpath": "/button3"},
                "selectorStrategies": {"css": "#btn3"},
                "extra": {}
            },
            {
                "pageUrl": "https://app.com/page",
                "action": "change",
                "type": "change",
                "timestamp": "2026-01-07T10:00:01.000000+00:00",  # First
                "element": {"tag": "input", "xpath": "/input1"},
                "selectorStrategies": {"css": "#input1"},
                "extra": {"value": "test"}
            },
            {
                "pageUrl": "https://app.com/page",
                "action": "click",
                "type": "click",
                "timestamp": "2026-01-07T10:00:02.000000+00:00",  # Second
                "element": {"tag": "button", "xpath": "/button2"},
                "selectorStrategies": {"css": "#btn2"},
                "extra": {}
            },
        ],
        "flowName": "Test Flow",
        "options": {},
        "pages": []
    }
    
    result = build_refined_flow_from_metadata(metadata)
    steps = result.get("steps", [])
    
    # Verify steps are in chronological order (sorted by timestamp)
    assert len(steps) == 3
    assert steps[0]["action"] == "Fill"  # First by timestamp (change->fill)
    assert steps[1]["action"] == "Click"  # Second
    assert steps[2]["action"] == "Click"  # Third


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
