# Manual Authentication Support - Implementation Summary

## Overview
Modified the Playwright test script generation to support manual authentication workflows. Instead of automated login via LoginPage, generated scripts now navigate to the original URL and wait for the user to complete authentication manually.

## Changes Made

### 1. Extract and Pass original_url Through the Pipeline

#### File: `app/agentic_script_agent.py`

**`_load_refined_flow_from_disk` method (lines ~807-835)**:
- Extract `original_url` from the top-level metadata of refined JSON files
- Add `original_url` field to each step dictionary returned

**`_steps_from_vector_docs` method (lines ~727-767)**:
- Extract `original_url` from vector DB metadata or payload
- Maintain `resolved_original_url` across all steps
- Add `original_url` field to each step dictionary returned

### 2. Modify Script Generation Logic

**Test spec generation (lines ~1770-1812)**:
- Extract `original_url` from first step in `step_refs`
- Find the first non-login element's selector key for waitFor statement
- **Always emit navigation step** at the beginning if `original_url` is present:
  ```typescript
  await page.goto("https://onecognizant.cognizant.com/Welcome");
  // Manual authentication: Complete login steps manually in the browser
  // Wait for first element after authentication
  await pageObject.firstElement.waitFor({ state: "visible", timeout: 60000 });
  ```
- Skip any remaining login steps (they should already be filtered by authentication filtering)

## Generated Script Example

```typescript
test.describe("qwerty", () => {
  let qwertypage: PageObject;
  
  run("qwerty", async ({ page }, testinfo) => {
    qwertypage = new PageObject(page);
    
    // Step 0 - Navigate and wait for manual auth
    await namedStep("Step 0 - Navigate to application and wait for manual authentication", page, testinfo, async () => {
      // Navigate to the original URL
      await page.goto("https://onecognizant.cognizant.com/Welcome");
      // Manual authentication: Complete login steps manually in the browser
      // Wait for first element after authentication
      await qwertypage.close.waitFor({ state: "visible", timeout: 60000 });
      const screenshot = await page.screenshot();
      attachScreenshot("Step 0 - Navigate to application and wait for manual authentication", testinfo, screenshot);
    });

    // Step 1 - Click the Close button
    await namedStep("Step 1 - Click the Close button", page, testinfo, async () => {
      await qwertypage.close.click();
      const screenshot = await page.screenshot();
      attachScreenshot("Step 1 - Click the Close button", testinfo, screenshot);
    });
    
    // ... remaining steps
  });
});
```

## Benefits

1. **Manual Authentication Support**: Users can manually complete complex authentication flows (OAuth, SSO, MFA) while the script waits
2. **No LoginPage Dependency**: Scripts no longer require a LoginPage object or automated credentials
3. **60-second Timeout**: Generous timeout (60000ms) allows time for multi-step authentication
4. **Clear Comments**: Generated code includes explicit comments about manual authentication
5. **Automatic Wait**: Waits for the first application element to appear, ensuring auth is complete before proceeding

## Testing

Created `test_script_generation.py` to verify:
- ✅ original_url is extracted from refined flow
- ✅ page.goto() with correct URL is present in generated script
- ✅ waitFor() with 60-second timeout is present
- ✅ Manual authentication comment is included
- ✅ First element selector is correctly identified

Test output:
```
✅ Found 11 vector steps
✅ Original URL from first step: https://onecognizant.cognizant.com/Welcome
✅ page.goto() with original URL found in generated script
✅ waitFor() with visible state found in generated script
✅ Manual authentication comment found
```

## Usage Instructions

1. **Record Your Flow**: Use the recorder as normal, including login steps
2. **Auto-Filtering**: Authentication steps are automatically filtered during refinement
3. **Generate Script**: Generate the Playwright script via the React UI or API
4. **Run Test**: 
   - Script will navigate to the original URL
   - Pause and wait (up to 60 seconds)
   - **Manually complete login** in the browser window
   - Once the first application element appears, the script continues automatically

## Related Files

- `app/agentic_script_agent.py`: Core script generation logic (modified)
- `app/recorder_auto_ingest.py`: Authentication filtering (existing)
- `app/ingest_refined_flow.py`: Stores original_url in vector DB (existing)
- `test_script_generation.py`: Verification test (new)

## Backward Compatibility

- If `original_url` is not present in the refined flow, the navigation step is skipped
- Existing LoginPage-based scripts continue to work (if LoginPage exists in framework repo)
- Auth filtering can be disabled if needed (though not recommended)

## Future Enhancements

- Add configurable timeout via environment variable or testmanager.xlsx
- Support multiple authentication checkpoints for complex multi-domain flows
- Add visual indicator or prompt during manual authentication wait period
