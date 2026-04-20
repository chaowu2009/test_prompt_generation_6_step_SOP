import streamlit as st

from sop_core import STEP_CONFIG, apply_global_styles, ensure_state

st.set_page_config(page_title="Java Test Framework SOP", layout="wide")

apply_global_styles()
ensure_state()

st.title("Java Test Framework SOP Prompt Generator")
st.caption("Use the left Pages menu to open step_0 through step_6. No dropdown is used.")

st.markdown("### Overall Progress")
for step_key, config in STEP_CONFIG.items():
    step_num = step_key.split("_")[-1]
    is_done = st.session_state.done_flags.get(step_key, False)
    status = "Done" if is_done else "Pending"
    st.write(f"- Step {step_num} ({config['name']}): {status}")
