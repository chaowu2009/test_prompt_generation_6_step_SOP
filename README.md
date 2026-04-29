# Prompt Generation 6-Step SOP

This project is a Streamlit app that helps generate prompt text for a structured 6-step SOP used in Java test framework workflows.

It provides:

1. A shared SOP context step.
2. Six sequential workflow steps: Clarify, Define, Map, Plan, Build, Close.
3. A standalone page to generate a SKILL.md authoring prompt.

## What This App Does

The app is a prompt generator, not an execution engine.

It collects user inputs for each SOP step and generates a text prompt that can be copied or downloaded. The generated prompts are intended to be used with an LLM or a manual review flow.

Core behavior:

1. Defines all step metadata centrally (role, task, inputs, outputs, rules, save target).
2. Renders one page per step using shared UI and state logic.
3. Builds step prompts in a consistent plain-text template.
4. Tracks per-step completion status in session state.

## Tech Stack

1. Python 3.x
2. Streamlit (see requirements.txt)

Dependencies:

1. streamlit>=1.35.0

## Project Structure

1. app.py
2. sop_core.py
3. pages/
4. requirements.txt

Main files:

1. app.py
	Entry page. Shows links to all workflow pages and overall step completion status.
2. sop_core.py
	Shared logic and configuration:
	1. Global CSS styling.
	2. SOP metadata and rules.
	3. Session state initialization.
	4. Form rendering and prompt building.
	5. Copy/download helpers.
3. pages/step_0_(Shared_Context).py ... pages/step_6_(Close).py
	Thin page wrappers that call the shared renderer with a step key.
4. pages/generate_SKILL_file.py
	Standalone page that outputs a prewritten prompt used to generate a repository-specific SKILL.md.

## Workflow Model

The configured sequence is:

1. Clarify
2. Define
3. Map
4. Plan
5. Build
6. Close

Step 0 provides shared context and baseline rules used by all downstream steps.

Each workflow step includes:

1. Role
2. Task
3. Inputs (required/optional/workflow artifact references)
4. Expected outputs
5. Rules
6. Save target filename

## Output Files Referenced by the SOP

The prompt templates reference these artifacts:

1. test_step_1_output.md
2. test_step_2_output.md
3. test_step_3_gherkin.feature
4. test_step_3_output.md
5. test_step_4_output.md
6. test_step_5_output.md
7. test_step_6_output.md

Important: this app does not write these files directly. It generates prompt text that instructs where content should be saved.

## How Prompt Generation Works

For each step page:

1. Fill input fields (or leave optional fields blank).
2. Click Generate.
3. Review generated prompt text.
4. Copy via button or download as .txt.
5. Clear fields when needed.

Done flags:

1. A step is considered done when prompt text exists for that step in session state.
2. The checkbox on each step page is display-only.
3. The home page shows pending/done status for all steps.

## Session State Keys

The app uses Streamlit session state keys managed in shared logic:

1. form_data
	Per-step field values.
2. generated_prompt_by_step
	Generated prompt text by step key.
3. done_flags
	Boolean completion indicator per step.
4. generate_skill_file_prompt
	Output text for the standalone SKILL prompt page.

## Run Locally

From the project root:

1. Create and activate a virtual environment.
2. Install dependencies.
3. Start Streamlit.

Example commands (PowerShell):

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

The app will open in a local browser tab, usually at a localhost URL shown in terminal output.

## Notes About Step Definitions

1. Validation for required inputs is intentionally non-blocking in current logic.
2. Workflow artifact references (for example test_step_2_output.md) can be auto-included as plain references when no manual value is provided.
3. Step 3 includes explicit Gherkin-focused rules in configuration, including insertion of # new step markers in new step locations.

## Customization Points

If you want to adapt the SOP:

1. Update STEP_CONFIG in sop_core.py to change step names, roles, inputs, outputs, rules, and save targets.
2. Update DEFAULT_RULES, MARKDOWN_STYLE, COMMON_INPUT_PLACEHOLDERS, and SHARED_CONTEXT in sop_core.py.
3. Update PROMPT_TEXT in pages/generate_SKILL_file.py for SKILL.md prompt behavior.

## Current Limitations

1. No persistence layer; state resets when Streamlit session resets.
2. No automatic writing of generated .md/.feature output files.
3. No built-in validation against real repository file existence.

## License

No license file is currently included in this repository.
"# prompt_generation_6_step_SOP" 
