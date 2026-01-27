# ESAN Video Narration Script - Text to Speech

## 0:00 - 0:37 (Home Page)

Welcome to ESAN, where artificial intelligence meets test automation.

Testing enterprise applications used to take weeks of manual work, but we've changed that.

Here on our home page, you'll see two powerful components: Recorder and Execute.

Let me show you how ESAN uses generative AI to turn hours of repetitive testing into minutes of intelligent automation.

## 0:37 - 0:57 (Starting Recording)

I'm clicking on the Record option to start capturing a workflow.

I'll provide some basic information like the workflow name and description.

Now watch as the Chromium browser launches automatically.

This is where the magic begins.

## 0:57 - 2:06 (User Recording Workflow)

Now I'm simply performing my task as I normally would, clicking buttons, filling forms, navigating pages.

Behind the scenes, ESAN uses Playwright technology to capture every single action in real time.

It's recording not just what I click, but also the DOM elements, which are the building blocks of web pages, so it knows exactly where each button and field is located.

The best part? No coding knowledge required.

Just do your job naturally, and our intelligent recorder captures everything with smart locators that can adapt even if the page design changes slightly.

## 2:06 - 2:13 (Manual or Automation Choice)

Recording complete.

Now here's where ESAN's dual agent AI system comes into play.

The system asks: do you want Manual test cases for documentation, or Automation scripts for execution?

I'll select Manual first to show you how our first AI agent works.

## 2:13 - 2:29 (Repository Details & New Script)

I'm providing repository details so ESAN knows where to store the generated code.

Think of a repository as a secure storage location for all your automation scripts, like a library for code.

Now it's asking: do you want to use an existing script or generate a new one?

Since this is a brand new workflow we just recorded, I'm selecting new script generation.

## 2:29 - 2:58 (Preview & Editing)

Here's the preview showing all the steps we just recorded.

Notice you can edit these steps if something needs adjustment, maybe you want to add a wait time or change a validation.

Here's the intelligent part: our Large Language Model, or LLM, which is the brain behind generative AI, considers your edits as feedback.

It learns from your changes and regenerates the script accordingly.

This is what we call Agentic AI, an autonomous system that learns and adapts based on your input, making the automation smarter with every interaction.

## 2:58 - 3:08 (Generated Script)

And here it is, the generated Playwright automation script.

This is production ready code, properly formatted and following industry best practices.

What would have taken a developer hours or even days to write manually, our AI generated in seconds.

Now let's look at the test manager Excel file, which is the key to our parallel execution capability.

## 3:08 - 3:33 (Test Data)

This test manager Excel file is where we define our execution details and test data.

Notice we've provided multiple rows of test data here.

Each row represents a different test scenario, maybe different user credentials, different reference IDs, or different business cases.

This is called data driven testing, where one script can test multiple scenarios by simply changing the input data.

## 3:33 - 3:44 (Parallel Execution Explanation)

Since we have multiple test data rows, ESAN's execution engine will run them in parallel.

Instead of testing one scenario, then waiting, then testing the next, we launch multiple browser instances simultaneously.

Each browser runs independently with its own test data.

This is how we achieve seventy percent faster execution compared to traditional sequential testing.

Let's launch the trial run and watch it in action.

## 3:44 - 4:39 (Trial Run Execution)

Trial run is launching.

Watch as multiple browser tabs open simultaneously, this is parallel execution in action.

Browser one is executing with its own dataset, maybe testing with user ID ten thousand five.

Browser two is running completely independently with different credentials, perhaps user ID ten thousand three.

Browser three is also executing in parallel with yet another dataset.

Each browser is performing the exact same recorded actions we captured earlier, but with unique test data.

This is the power of parallel processing.

What used to take thirty minutes running tests one by one now takes just nine minutes, a seventy percent reduction in execution time.

And the best part? Each execution is completely isolated, so they don't interfere with each other.

## 4:39 - 4:48 (Success & Git Push)

Trial run success!

All parallel executions completed successfully, every test passed.

Now I'm pushing the changes to Git, which is a version control system.

Think of it like saving different versions of a document, but for code.

This means our automation script is now safely stored, version controlled, and ready for production use.

Anyone on the team can access it, and we have a complete history of all changes.

## 4:48 - 5:02 (Next Steps - Manual Test Generation)

Moving to the next step.

ESAN shows two options: generate manual test cases for documentation, or complete the task.

Remember I mentioned our dual agent AI system earlier?

We've just seen Agent Two create the automation script.

Now let me show you Agent One by selecting generate manual test cases.

This demonstrates how one recording gives you both automation and documentation.

## 5:02 - 5:29 (Manual Test Case Generation)

I'm uploading a template that defines the format we want for our test cases.

Clicking generate.

Now our first AI agent, powered by a Large Language Model, is analyzing the entire workflow we recorded.

It's not just copying what we did, it's understanding the intent and generating comprehensive test cases.

This includes positive scenarios where everything works correctly, negative scenarios where we test error handling, and edge cases for unusual situations.

The AI is essentially thinking like a QA engineer, anticipating what could go wrong and how to test for it.

And there it is, the test sheet is ready and downloadable.

## 5:29 - 5:56 (Test Sheet Preview)

Opening the generated test sheet.

Look at this, detailed test cases with clear descriptions, step by step instructions, expected results, and test data.

Each test case is comprehensive and ready to share with your team or stakeholders.

And remember, all of this was generated automatically from our single recording.

No manual writing, no hours spent documenting.

This is the power of our dual agent AI system: Agent One creates human readable documentation, Agent Two creates executable automation scripts, both from the same recording.

## 5:56 - 6:04 (Navigate to Execute)

Returning to the home page.

Now let me show you the Execute component, which is where you run your automation scripts on demand.

Clicking Execute.

Selecting automation test script.

This is useful when you want to run existing tests with new data or retest after application changes.

## 6:04 - 6:19 (Execute Setup)

I'm selecting the workflow we just recorded and automated.

Providing repository details so ESAN can fetch the latest version of the script from our code repository.

This ensures we're always running the most up to date automation.

In choose your path, I'm selecting use existing script since we already generated one earlier.

This shows how easy it is to reuse automation scripts for regression testing or continuous testing.

## 6:19 - 6:36 (Execution Details)

Now I'm updating the execution details with fresh test data.

Maybe I want to test with different user accounts, or different business scenarios, or different environments.

Notice how easy it is to run the exact same automation script with completely different datasets.

This is the beauty of data driven testing, one script, unlimited test scenarios.

## 6:36 - 7:03 (Final Execution)

Execution is starting.

Multiple browsers are launching in parallel once again.

Each browser is running the same test but with its own unique test data.

This is data driven testing at enterprise scale.

While the tests run, ESAN automatically captures everything: test results, screenshots for visual verification, and execution traces for debugging.

Everything aggregates into a unified dashboard where you can see pass fail status, execution time, and detailed reports.

And that's ESAN in action.

Capture your workflow once using our intelligent recorder.

Our dual agent AI system generates both documentation and automation.

Run tests in parallel with different data, cutting execution time by seventy percent.

Get instant results with comprehensive reports.

All powered by generative AI, Large Language Models, and intelligent automation.

No coding required, just record, generate, and execute.

Thank you for watching.

---

## ALTERNATIVE: Shorter Technical Narration (If Needed)

### 0:00 - 2:06
Welcome to ESAN. I'm starting a recording by clicking Record and providing details. Chromium launches. Now I'm performing the manual workflow. Playwright captures every action with smart locators.

### 2:06 - 2:58
Recording complete. Selecting Manual path. Providing repo details. Choosing new script generation. Here's the preview where I can edit steps. The LLM uses this feedback.

### 2:58 - 3:44
Generated script is ready. The test manager Excel has multiple test data rows. This enables parallel execution. Launching trial run.

### 3:44 - 4:48
Multiple browsers executing in parallel, each with different test data. Seventy percent faster execution. Trial run success. Pushing to Git.

### 4:48 - 5:56
Generating manual test cases. Uploading template. LLM creates positive, negative, and edge case scenarios. Test sheet is downloadable. Here's the preview.

### 5:56 - 7:03
Back to home. Clicking Execute. Selecting automation script and workflow. Using existing script. Updating execution details with different test data. Execution starts with parallel browsers. Results captured automatically. That's ESAN.

---

## Tips for Recording
- Speak clearly and at moderate pace
- Pause between major sections (new paragraphs)
- Emphasize: "dual agent", "parallel execution", "seventy percent faster", "no coding required"
- Match narration timing to video actions
- Use natural tone, not robotic
