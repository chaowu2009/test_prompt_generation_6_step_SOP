import streamlit as st

from sop_core import render_step_page

st.set_page_config(page_title="SOP Step 0", layout="wide")
render_step_page("step_0")
