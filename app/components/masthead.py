import streamlit as st

from constants import ASSETS_DIR


def render_masthead() -> None:
    """Logo (if app/assets/logo.png exists) + the journal-style title block."""
    logo = ASSETS_DIR / 'logo.png'
    if logo.exists():
        lc1, lc2, lc3 = st.columns([1, 1, 1])
        with lc2:
            st.image(str(logo), width='stretch')

    st.markdown(
        """
        <div class="masthead">
            <div class="eyebrow">Clinical Decision Support System &nbsp;·&nbsp; Explainable AI</div>
            <h1>Stroke &amp; Cardiovascular Disease Risk Assessment</h1>
            <div class="subtitle">A machine-learning tool with SHAP-based transparency for individual risk estimation</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
