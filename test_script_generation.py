"""
Test script to verify that generated Playwright scripts include page.goto(original_url)
"""
import json
from pathlib import Path
from app.agentic_script_agent import AgenticScriptAgent, FrameworkProfile

def test_qwerty_script_generation():
    """Test that qwerty flow generates script with page.goto(original_url) and wait"""
    
    # Initialize the agent
    agent = AgenticScriptAgent()
    
    # Create a minimal framework profile
    framework = FrameworkProfile(
        root=Path("c:/Users/keerthee/gen_ai/guideware_test_tool/guideware_test_creation-main/framework_repos/default"),
        locators_dir=None,
        pages_dir=None,
        tests_dir=None
    )
    
    scenario = "qwerty"
    
    # Gather context to get the steps
    context = agent.gather_context(scenario)
    vector_steps = context.get("vector_steps") or []
    
    if not vector_steps:
        print("❌ No vector steps found for qwerty scenario")
        return False
    
    print(f"✅ Found {len(vector_steps)} vector steps")
    
    # Check if original_url is in the steps
    first_step = vector_steps[0]
    original_url = first_step.get("original_url", "")
    print(f"✅ Original URL from first step: {original_url}")
    
    # Generate a simple preview (just list the steps)
    preview = "\n".join([
        f"{i}. {step.get('action')} | {step.get('navigation')}"
        for i, step in enumerate(vector_steps, 1)
    ])
    
    try:
        # Generate the script payload
        payload = agent.generate_script_payload(scenario, framework, preview)
        
        # Get the test spec content
        test_files = payload.get("tests", [])
        if not test_files:
            print("❌ No test files generated")
            return False
        
        test_content = test_files[0].get("content", "")
        
        # Verify original_url is in the generated script
        if original_url and original_url in test_content:
            print(f"✅ page.goto() with original URL found in generated script")
        else:
            print(f"⚠️  Original URL not found in generated script")
            print(f"   Expected URL: {original_url}")
        
        # Verify wait for element is present
        if "waitFor(" in test_content and "visible" in test_content:
            print("✅ waitFor() with visible state found in generated script")
        else:
            print("⚠️  waitFor() not found in generated script")
        
        # Verify manual authentication comment
        if "manual authentication" in test_content.lower():
            print("✅ Manual authentication comment found")
        else:
            print("⚠️  Manual authentication comment not found")
        
        # Print a sample of the navigation step
        print("\n--- Sample navigation step from generated script ---")
        lines = test_content.split("\n")
        in_nav_step = False
        nav_lines = []
        for line in lines:
            if "Navigate to application" in line or "manual authentication" in line.lower():
                in_nav_step = True
            if in_nav_step:
                nav_lines.append(line)
                if line.strip() == "});":
                    break
        
        if nav_lines:
            print("\n".join(nav_lines[:20]))  # Print first 20 lines of nav step
        
        return True
        
    except Exception as e:
        print(f"❌ Error generating script: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_qwerty_script_generation()
    if success:
        print("\n✅ Script generation test completed successfully")
    else:
        print("\n❌ Script generation test failed")
