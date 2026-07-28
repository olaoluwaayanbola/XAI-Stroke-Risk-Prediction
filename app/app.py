import streamlit as st

from styles import inject_css
from prediction import run_prediction
from components.masthead import render_masthead
from components.sidebar import render_sidebar, render_session_history
from components.summary_results import render_summary_and_results
from components.explanation import render_explanation
from components.simulator import render_simulator
from components.lime_panel import render_lime_panel
from components.trust_dashboard import render_trust_dashboard

# --------------------------------------------------------------------------- #
# Page configuration
# --------------------------------------------------------------------------- #
st.set_page_config(
    page_title='Stroke / CVD Risk — Clinical Decision Support',
    layout='wide',
)

inject_css()
render_masthead()

# --------------------------------------------------------------------------- #
# Sidebar — patient data entry + clinical flags
# --------------------------------------------------------------------------- #
inputs, predict_btn = render_sidebar()

# On click, compute the prediction once and stash it — together with a snapshot
# of the inputs that produced it — so the result panel can tell whether the
# sidebar has since changed and the displayed number is stale.
if predict_btn:
    run_prediction(inputs)

render_session_history()

result = st.session_state.get('result')
stale  = result is not None and st.session_state.get('result_inputs') != inputs

# --------------------------------------------------------------------------- #
# Main body — patient summary + risk assessment, SHAP explanation, PDF export,
# what-if simulator, LIME validation, model trust dashboard
# --------------------------------------------------------------------------- #
render_summary_and_results(inputs, result, stale)
render_explanation(inputs, result)
render_simulator(inputs, result)
render_lime_panel(result)
render_trust_dashboard()

# --------------------------------------------------------------------------- #
# Footer
# --------------------------------------------------------------------------- #
st.markdown(
    """
    <div class="app-footer">
        Research and educational use only — not a substitute for professional clinical judgement.<br>
        Explainable AI · Cardiovascular Risk Modelling
    </div>
    """,
    unsafe_allow_html=True,
)
