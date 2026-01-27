"""
Generate and save a sample Playwright script for the qwerty scenario
"""
from pathlib import Path
from app.agentic_script_agent import AgenticScriptAgent, FrameworkProfile

def generate_qwerty_sample():
    """Generate a sample Playwright script for qwerty flow"""
    
    agent = AgenticScriptAgent()
    framework = FrameworkProfile(
        root=Path("c:/Users/keerthee/gen_ai/guideware_test_tool/guideware_test_creation-main/framework_repos/default"),
        locators_dir=None,
        pages_dir=None,
        tests_dir=None
    )
    
    scenario = "qwerty"
    context = agent.gather_context(scenario)
    vector_steps = context.get("vector_steps") or []
    
    if not vector_steps:
        print("❌ No vector steps found")
        return
    
    # Generate preview
    preview = "\n".join([
        f"{i}. {step.get('action')} | {step.get('navigation')}"
        for i, step in enumerate(vector_steps, 1)
    ])
    
    # Generate script
    payload = agent.generate_script_payload(scenario, framework, preview)
    test_files = payload.get("tests", [])
    
    if test_files:
        test_content = test_files[0].get("content", "")
        output_path = Path("qwerty_generated_sample.spec.ts")
        output_path.write_text(test_content, encoding="utf-8")
        print(f"✅ Generated script saved to: {output_path}")
        print(f"\n📝 Script size: {len(test_content)} characters")
        print(f"📝 Number of steps: {len(vector_steps)}")
        
        # Show first 50 lines
        lines = test_content.split("\n")
        print("\n--- First 50 lines of generated script ---\n")
        for i, line in enumerate(lines[:50], 1):
            print(f"{i:3}: {line}")
    else:
        print("❌ No test files generated")

if __name__ == "__main__":
    generate_qwerty_sample()
