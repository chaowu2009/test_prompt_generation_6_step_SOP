import json
import html
import re
from pathlib import Path
from typing import Any, Dict, List

import streamlit as st


BASE_DIR = Path(__file__).resolve().parent


def apply_global_styles() -> None:
    st.markdown(
        """
<style>
.stApp, .stApp * {
    font-size: 12pt !important;
}

.stApp {
    background: linear-gradient(180deg, #f6f8fc 0%, #eef3fb 100%);
}

h1 {
    color: #173b63;
    letter-spacing: 0.2px;
}

h2 {
    color: #4f9cff;
    letter-spacing: 0.2px;
}

h3 {
    color: #173b63;
    letter-spacing: 0.2px;
}

[data-testid="stCaptionContainer"] {
    background: #e7f0ff;
    border: 1px solid #c8dcff;
    border-radius: 10px;
    padding: 8px 10px;
}

.sop-field-label {
    font-weight: 700;
    color: #173b63;
    margin: 8px 0 4px;
}

.sop-file-name {
    display: inline-block;
    color: #1d5fd1;
    background: #e7f0ff;
    border: 1px solid #c8dcff;
    border-radius: 6px;
    padding: 0 6px;
    font-weight: 700;
}

.sop-rich-line {
    margin: 0.2rem 0;
}

.sop-prompt-preview {
    max-height: 420px;
    overflow: auto;
    white-space: pre-wrap;
    color: #173b63;
}

[data-testid="stTextArea"] textarea {
    border: 1px solid #bdd0ee !important;
    border-radius: 10px !important;
    background: #ffffff !important;
}

[data-testid="stTextArea"] textarea:focus {
    border-color: #2e6fd8 !important;
    box-shadow: 0 0 0 2px rgba(46, 111, 216, 0.15) !important;
}

.stButton > button,
.stDownloadButton > button {
    border-radius: 10px !important;
    border: 1px solid #2e6fd8 !important;
}

.stButton > button[kind="primary"] {
    background: linear-gradient(90deg, #2e6fd8 0%, #2f8dbf 100%) !important;
    color: #ffffff !important;
}

.stButton > button:hover,
.stDownloadButton > button:hover {
    filter: brightness(0.98);
}
</style>
""",
        unsafe_allow_html=True,
    )

SOP_TITLE = "Daily-Use 6-Step SOP for Java Test Development"

SHARED_CONTEXT = {
    "team_context": "You are supporting a QA automation team delivering website solutions in a safe agile environment.",
    "sequence": "Clarify -> Define -> Map -> Plan -> Build -> Close",
    "stack": "This SOP supports a test stack based on Java, Cucumber, TestNG, Selenium, and Xray.",
}

DEFAULT_RULES = [
    "Use SKILL.md if available throughout each SOP step as the primary source for reusable workflow patterns and conventions whenever available. Recheck it before finalizing outputs. If it conflicts with current confirmed story inputs or 3-amigos decisions, prioritize current confirmed inputs and note the conflict.",
    "use the latest referenced .md file as the source of truth",
    "after each step, the user may review and revise the generated .md file",
    "each next step must use the latest reviewed .md file as the source of truth",
    "if a reviewed file changes direction, refresh affected downstream steps before continuing",
    "reuse existing assets first",
    "prefer lower stable coverage before Selenium UI coverage when valid",
    "do not invent missing facts",
    "do not fix unrelated existing issues unless they directly impact the current issue, current test coverage, or current execution",
    "do not use Thread.Sleep() or similar hard waits",
    "use 3 amigos only when requirements, scope, or expected behavior are unclear",
    "when temporary, fake, sample, placeholder, stubbed, mocked, hardcoded, skipped, or bypassed items are found, record them under a dedicated ## Temporary, Placeholder, or Risky Items section in the generated .md output when relevant",
]

MARKDOWN_STYLE = [
    "keep .md output light and easy to scan",
    "use one # title and ## sections",
    "prefer short bullets and short paragraphs",
    "use fenced code blocks with language tags when needed",
    "label Assumptions, Risks, Dependencies, and Open Questions when relevant",
]

COMMON_INPUT_PLACEHOLDERS = [
    "Jira / story / notes",
    "expected behavior",
    "actual behavior",
    "screenshots / logs / errors",
    "existing files / classes / methods to reuse",
    "target file path or package if known",
    "3 amigos notes if available",
]

STEP_CONFIG: Dict[str, Dict[str, Any]] = {
    "step_0": {
        "name": "Shared Context",
        "role": "SOP Coordinator",
        "task": "Provide the baseline context and reusable references for all downstream steps.",
        "inputs": [
            "additional shared context notes",
        ],
        "outputs": [
            "Shared context package used by later steps",
        ],
        "rules": [
            "Do not generate implementation output in Step 0.",
        ],
        "save_to": "(no required output file)",
    },
    "step_1": {
        "name": "Clarify",
        "role": "Senior Test Analyst",
        "task": "Turn raw story and discussion input into a clear test-ready summary.",
        "inputs": [
            "Jira / AC / notes",
            "logs / errors / screenshots text",
            "expected behavior",
            "actual behavior",
            "impacted area",
            "known existing coverage or reuse",
            "3 amigos notes if available",
        ],
        "outputs": [
            "business objective",
            "scope / out of scope",
            "assumptions / open questions",
            "impacted areas / dependencies / risks",
            "reuse candidates",
            "recommended test approach",
        ],
        "rules": [
            "facts first",
            "improve clarity, not meaning",
            "preserve confirmed 3-amigos decisions",
            "if business behavior or scope is unclear, recommend 3 amigos follow-up",
        ],
        "save_to": "test_step_1_output.md",
    },
    "step_2": {
        "name": "Define",
        "role": "Test Architect",
        "task": "Turn Step 1 output into clear acceptance criteria and test conditions.",
        "inputs": "test_step_1_output.md",
        "outputs": [
            "acceptance criteria",
            "positive / negative / edge scenarios",
            "regression / accessibility / content checks",
            "automation vs manual recommendation",
            "deferred / out-of-scope items",
        ],
        "rules": [
            "observable outcomes only",
            "no implementation details",
            "no code",
            "if ACs cannot be made testable from available facts, recommend 3 amigos follow-up",
        ],
        "save_to": "test_step_2_output.md",
    },
    "step_3": {
        "name": "Map",
        "role": "Senior Test Automation Architect",
        "task": "Map coverage across the current stack: Java, Cucumber, TestNG, Selenium, and Xray.",
        "inputs":"test_step_2_output.md",
        "optional_inputs": [
            "existing files / classes / methods to reuse",
            "target file path or package if known",
            "sample gherkin content",
        ],
        "outputs": [
            "Gherkin file in test_step_3_gherkin.feature",
            "layer strategy",
            "AC-to-test-layer mapping",
            "manual vs automated split",
            "reuse candidates",
            "impacted assets",
            "risks and gaps"
        ],
        "rules": [
            "you need think of work flow from existing gherkin scenarios for a document review process, starting from log in.", 
            "existing gherkins may come from file existing_gherkin_file.feature or from given prompts",
            f"add a new line \"# new step\" exactly on top of every new step in \"test_step_3_gherkin.feature\" file, double check it. you many have many places to insert such line",
            "add a section in \"test_step_3_output.md\" to summerize new steps created, double check it.",
            "choose the lowest stable layer first",
            "use Selenium only when UI coverage is truly needed",
            "cover every AC without bloating scenarios",
            "name reuse options before suggesting new assets",
        ],
        "save_to": "test_step_3_output.md",
    },
    "step_4": {
        "name": "Plan",
        "role": "Senior Test Automation Lead",
        "task": "Plan the minimum framework changes needed to implement Step 3.",
        "inputs": [
            "test_step_3_output.md",
            "test_step_3_gherkin.feature",
        ],
        "optional_inputs": [
            "target classes / methods / file paths if known",
        ],
        "outputs": [
            "implementation scope",
            "classes and methods to update",
            "file paths / package paths",
            "test data updates",
            "reuse plan",
            "local / grid impact",
            "Xray update needs",
            "risks or blockers",
        ],
        "rules": [
            "no Gherkin work in this step",
            "no full Java code yet",
            "extend existing assets first",
            "keep changes minimal and parallel-safe",
        ],
        "save_to": "test_step_4_output.md",
    },
    "step_5": {
        "name": "Build",
        "role": "Senior Test Automation Engineer",
        "task": "Implement the minimum approved automation changes from Step 4.",
        "inputs": "test_step_4_output.md",
        "optional_inputs": [
            "exact files / methods / data / logs if known",
        ],
        "outputs": [
            "feature file updates if approved and required",
            "code changes",
            "files changed",
            "methods changed",
            "local / grid execution commands",
            "validation results",
            "Temporary, Placeholder, or Risky Items",
            "deferred items",
        ],
        "rules": [
            "Never create a file unless it contains complete, functional content. Do not create placeholder classes, stub methods with only a TODO body, empty config files, or empty directories. If a file cannot be fully implemented in the current step, skip it and note it as pending instead.",
            "modify existing assets first",
            "no unrelated refactoring or unrelated bug fixing",
            "verify local and grid when required",
            "separate implemented work from follow-up recommendations",
        ],
        "save_to": "test_step_5_output.md",
    },
    "step_6": {
        "name": "Close",
        "role": "Test Lead",
        "task": "Create the closure report using the defined test baseline, implementation results, and execution evidence.",
        "inputs": [
            "test_step_2_output.md",
            "test_step_5_output.md",
        ],
        "optional_inputs": [
            "execution results / logs / screenshots / CI summary / Xray updates",
        ],
        "outputs": [
            "AC validation",
            "automated / manual coverage summary",
            "execution status",
            "Xray traceability",
            "Temporary, Placeholder, or Risky Items",
            "risks / gaps / deferred items",
            "release recommendation",
            "Jira-ready closure comment",
        ],
        "rules": [
            "evidence only",
            "separate confirmed results from assumptions",
            "distinguish product issues from flaky or environment issues",
            "do not overstate completion",
        ],
        "save_to": "test_step_6_output.md",
    },
}


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", value.strip().lower())
    return slug.strip("_")


def default_field_value(field: str) -> str:
    return f"[{field}]"


FILE_NAME_PATTERN = re.compile(r"(?<![\w/\\.-])([A-Za-z0-9_().-]+\.(?:md|feature|txt))(?![\w/\\-])")


def highlight_file_names(text: str) -> str:
    escaped = html.escape(text)

    def replace_match(match: re.Match[str]) -> str:
        return f"<span class='sop-file-name'>{match.group(1)}</span>"

    return FILE_NAME_PATTERN.sub(replace_match, escaped)


def render_rich_text_line(text: str, prefix: str = "") -> None:
    content = highlight_file_names(text)
    prefix_html = html.escape(prefix)
    st.markdown(
        f"<div class='sop-rich-line'>{prefix_html}{content}</div>",
        unsafe_allow_html=True,
    )


def is_workflow_artifact_input(field: str) -> bool:
    normalized = field.strip()
    return bool(re.fullmatch(r"test_step_[1-6]_output\.md", normalized)) or normalized == "test_step_3_gherkin.feature"


def get_effective_field_value(step_key: str, field: str) -> str:
    field_key = slugify(field)
    value = st.session_state.form_data.get(step_key, {}).get(field_key, "")
    return str(value).strip()


def resolve_input_for_prompt(step_key: str, field: str) -> str:
    direct_value = get_effective_field_value(step_key, field)
    if direct_value:
        return direct_value

    normalized = field.strip()
    return normalized


def normalize_fields(fields: Any) -> List[str]:
    if isinstance(fields, str):
        stripped = fields.strip()
        return [stripped] if stripped else []
    if isinstance(fields, list):
        return [str(item).strip() for item in fields if str(item).strip()]
    return []


def get_step_inputs(step_key: str) -> List[str]:
    return normalize_fields(STEP_CONFIG[step_key].get("inputs"))


def get_step_optional_inputs(step_key: str) -> List[str]:
    return normalize_fields(STEP_CONFIG[step_key].get("optional_inputs"))


def ensure_state() -> None:
    if "form_data" not in st.session_state:
        st.session_state.form_data = {step_key: {} for step_key in STEP_CONFIG.keys()}

    for step_key, _config in STEP_CONFIG.items():
        if step_key not in st.session_state.form_data:
            st.session_state.form_data[step_key] = {}
        editable_fields = get_step_inputs(step_key) + get_step_optional_inputs(step_key)
        for field in editable_fields:
            field_key = slugify(field)
            if field_key not in st.session_state.form_data[step_key]:
                st.session_state.form_data[step_key][field_key] = ""

    if "generated_prompt_by_step" not in st.session_state:
        st.session_state.generated_prompt_by_step = {step_key: "" for step_key in STEP_CONFIG.keys()}

    if "done_flags" not in st.session_state:
        st.session_state.done_flags = {step_key: False for step_key in STEP_CONFIG.keys()}

    for step_key in STEP_CONFIG.keys():
        prompt_text = st.session_state.generated_prompt_by_step.get(step_key, "")
        if str(prompt_text).strip():
            st.session_state.done_flags[step_key] = True


def build_done_subtitle() -> str:
    parts: List[str] = []
    for step_key in STEP_CONFIG.keys():
        step_num = step_key.split("_")[-1]
        is_done = st.session_state.done_flags.get(step_key, False)
        if is_done:
            parts.append(f"Step {step_num} (Done)")
        else:
            parts.append(f"Step {step_num}")
    return ", ".join(parts)


def reset_step_fields(step_key: str) -> None:
    st.session_state.form_data[step_key] = {}
    editable_fields = get_step_inputs(step_key) + get_step_optional_inputs(step_key)
    for field in editable_fields:
        field_key = slugify(field)
        st.session_state.form_data[step_key][field_key] = ""
        state_key = f"{step_key}_{slugify(field)}"
        st.session_state[state_key] = ""


def _render_field(step_key: str, field: str, required: bool) -> None:
    field_key = slugify(field)
    state_key = f"{step_key}_{field_key}"
    current_value = st.session_state.form_data[step_key].get(field_key, "")
    label = f"{field} *" if required else field
    st.markdown(
        f"<div class='sop-field-label'>{highlight_file_names(label)}</div>",
        unsafe_allow_html=True,
    )
    entered = st.text_area(
        label=label,
        key=state_key,
        value=current_value,
        height=110,
        placeholder=f"Paste {field} content here..." if required else f"Optional — {field}",
        label_visibility="collapsed",
    )
    st.session_state.form_data[step_key][field_key] = entered


def render_step_form(step_key: str) -> None:
    config = STEP_CONFIG[step_key]
    st.subheader(f"{step_key.upper()} - {config['name']}")
    st.write(f"Role: {config['role']}")
    st.write(f"Task: {config['task']}")

    step_inputs = get_step_inputs(step_key)
    step_optional_inputs = get_step_optional_inputs(step_key)

    workflow_inputs = [field for field in step_inputs if is_workflow_artifact_input(field)]
    editable_inputs = [field for field in step_inputs if not is_workflow_artifact_input(field)]

    if workflow_inputs:
        st.markdown("### Input")
        for field in workflow_inputs:
            render_rich_text_line(field, prefix="- ")

    if editable_inputs:
        st.markdown("### Input Fields")
        st.caption("Fill these fields to include details in the generated prompt.")
        for field in editable_inputs:
            _render_field(step_key, field, required=False)

    if step_optional_inputs:
        st.markdown("### Input Placeholders")
        st.caption("Optional — leave blank to omit from the generated prompt.")
        for field in step_optional_inputs:
            _render_field(step_key, field, required=False)


def validate_required_inputs(step_key: str) -> List[str]:
    # Prompt generation is intentionally non-blocking.
    # Workflow artifact inputs can be left blank while drafting prompts.
    return []


def build_step_0_prompt() -> str:
    lines: List[str] = []
    lines.append(SHARED_CONTEXT["team_context"])
    lines.append("")
    lines.append("This is a sequential 6-step SOP:")
    lines.append("")
    lines.append(SHARED_CONTEXT["sequence"])
    lines.append("")
    lines.append(SHARED_CONTEXT["stack"])
    lines.append("")

    lines.append("Default rules for all steps")
    lines.append("")
    for item in DEFAULT_RULES:
        lines.append(f"- {item}")
    lines.append("")

    lines.append("Markdown style")
    lines.append("")
    for item in MARKDOWN_STYLE:
        lines.append(f"- {item}")
    lines.append("")

    lines.append("Common input placeholders")
    lines.append("")
    for item in COMMON_INPUT_PLACEHOLDERS:
        lines.append(f"- [{item}]")
    lines.append("")

    notes_value = get_effective_field_value("step_0", "additional shared context notes")
    if notes_value:
        lines.append("Additional shared context notes")
        lines.append("")
        lines.append(notes_value)
        lines.append("")

    lines.append("Do not do anything yet.")
    return "\n".join(lines).strip() + "\n"


def build_step_prompt(step_key: str) -> str:
    config = STEP_CONFIG[step_key]

    lines: List[str] = []
    lines.append(f"Role: {config['role']}")
    lines.append("")
    lines.append(f"Task: {config['task']}")
    lines.append("")

    lines.append("Input")
    lines.append("")
    step_inputs = get_step_inputs(step_key)
    step_optional_inputs = get_step_optional_inputs(step_key)

    for item in step_inputs:
        value = resolve_input_for_prompt(step_key, item)
        if value:
            lines.append(f"- {value}")

    for item in step_optional_inputs:
        value = get_effective_field_value(step_key, item)
        if value:
            lines.append(f"- {value}")
    lines.append("")

    lines.append("Output")
    lines.append("")
    for item in config["outputs"]:
        lines.append(f"- {item}")
    lines.append("")

    lines.append("Rules")
    lines.append("")
    for item in config["rules"]:
        lines.append(f"- {item}")
    lines.append("")

    lines.append(f"Save to: {config['save_to']}")
    return "\n".join(lines).strip() + "\n"


def build_prompt(current_step_key: str) -> str:
    if current_step_key == "step_0":
        return build_step_0_prompt()
    if current_step_key in {"step_1", "step_2", "step_3", "step_4", "step_5", "step_6"}:
        return build_step_prompt(current_step_key)
    return ""


def render_prompt_preview(text: str) -> None:
    preview_html = highlight_file_names(text) if text else ""
    st.markdown(
        f"<div class='sop-prompt-preview'>{preview_html}</div>",
        unsafe_allow_html=True,
    )


def render_copy_button(step_key: str, text: str) -> None:
        button_id = f"copy-btn-{step_key}"
        escaped_text = json.dumps(text)
        disabled_attr = "disabled" if not text else ""

        st.components.v1.html(
                f"""
<div>
    <button id="{button_id}" {disabled_attr}
        style="
            width: auto;
            min-width: 96px;
            height: 2.5rem;
            border-radius: 10px;
            border: 1px solid #de8a8a;
            padding: 0 0.9rem;
            background: linear-gradient(90deg, #f7caca 0%, #f3b5b5 100%);
            color: #7a1f1f;
            font-weight: 600;
            cursor: pointer;
        ">
        Copy
    </button>
</div>
<script>
    (function() {{
        const btn = document.getElementById({json.dumps(button_id)});
        const text = {escaped_text};
        if (!btn) return;
        btn.addEventListener('mouseenter', function() {{
            if (!btn.disabled) btn.style.filter = 'brightness(0.98)';
        }});
        btn.addEventListener('mouseleave', function() {{
            btn.style.filter = 'none';
        }});
        if (btn.disabled) {{
            btn.style.opacity = '0.55';
            btn.style.cursor = 'not-allowed';
        }}
        btn.addEventListener('click', async function() {{
            const originalText = btn.textContent;
            try {{
                await navigator.clipboard.writeText(text);
                btn.textContent = 'Copied';
            }} catch (err) {{
                const ta = document.createElement('textarea');
                ta.value = text;
                document.body.appendChild(ta);
                ta.select();
                try {{
                    document.execCommand('copy');
                    btn.textContent = 'Copied';
                }} finally {{
                    document.body.removeChild(ta);
                }}
            }}
            setTimeout(function() {{ btn.textContent = originalText; }}, 1200);
        }});
    }})();
</script>
""",
                height=44,
        )


def render_step_page(step_key: str) -> None:
    apply_global_styles()
    ensure_state()
    config = STEP_CONFIG[step_key]

    st.title(f"{step_key.upper()} - {config['name']}")
    st.caption(build_done_subtitle())
    st.caption("Use Generate to build the prompt. Done flag is set automatically per step.")

    render_step_form(step_key)

    left_col, right_col, status_col = st.columns([1, 1, 1])
    with left_col:
        if st.button("Generate", type="primary", key=f"generate_{step_key}"):
            missing_required = validate_required_inputs(step_key)
            if missing_required:
                missing_display = ", ".join(missing_required)
                st.error(f"Required input missing: {missing_display}")
                st.session_state.done_flags[step_key] = False
                return
            st.session_state.generated_prompt_by_step[step_key] = build_prompt(step_key)
            st.session_state.done_flags[step_key] = True
    with right_col:
        if st.button("Clear Current Step Fields", key=f"clear_{step_key}"):
            reset_step_fields(step_key)
            st.session_state.generated_prompt_by_step[step_key] = ""
            st.session_state.done_flags[step_key] = False
            st.rerun()
    with status_col:
        st.checkbox("Done", value=st.session_state.done_flags[step_key], disabled=True, key=f"done_{step_key}")

    st.markdown("### Prompt Output")
    render_prompt_preview(st.session_state.generated_prompt_by_step[step_key])
    st.text_area(
        "Generated Prompt",
        value=st.session_state.generated_prompt_by_step[step_key],
        height=420,
    )

    output_copy_col, output_download_col = st.columns([1, 1])
    with output_copy_col:
        render_copy_button(step_key, st.session_state.generated_prompt_by_step[step_key])
    with output_download_col:
        st.download_button(
            label="Download Prompt (.txt)",
            data=st.session_state.generated_prompt_by_step[step_key].encode("utf-8"),
            file_name=f"{step_key}_prompt.txt",
            mime="text/plain",
            key=f"download_{step_key}",
        )
