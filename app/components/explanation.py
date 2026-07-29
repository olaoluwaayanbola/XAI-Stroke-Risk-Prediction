from __future__ import annotations

from datetime import datetime

import shap
import streamlit as st
import matplotlib.pyplot as plt

from constants import PatientInputs, risk_tier
from model import features
from pdf_report import REPORTLAB_AVAILABLE, generate_pdf_report


def render_explanation(inputs: PatientInputs, result: dict | None) -> None:
    """SHAP waterfall figure (full width) + the PDF export button. No-op
    until a prediction has been run.
    """
    if result is None:
        return

    st.markdown('<div style="height:1.4rem"></div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-label">Figure 1 — Why? Model Explanation (SHAP)</div>', unsafe_allow_html=True)
    st.write(
        'The waterfall plot below decomposes the prediction, showing how each patient '
        'feature pushes the estimated risk above or below the population baseline. '
        'Red bars increase the risk; blue bars decrease it.'
    )

    exp = shap.Explanation(
        values=result['shap_values'],
        base_values=result['base_value'],
        data=result['data'],
        feature_names=features,
    )
    plt.close('all')
    try:
        shap.plots.waterfall(exp, show=False)
        fig = plt.gcf()
        fig.patch.set_facecolor('#fbfaf7')
        st.pyplot(fig, clear_figure=False)
        st.session_state['shap_fig'] = fig
        st.markdown(
            '<div class="figure-caption">Figure 1. Per-feature SHAP contributions to the individual risk estimate.</div>',
            unsafe_allow_html=True,
        )
    except Exception:
        # shap.plots.waterfall is a third-party matplotlib call whose internal
        # tick-label handling has known environment-specific failure modes
        # (e.g. shap/shap#3553, streamlit/streamlit#15326-adjacent version
        # drift on Streamlit Cloud). Degrade gracefully rather than taking
        # the rest of the page down with it.
        st.session_state['shap_fig'] = None
        st.warning('SHAP waterfall visualization unavailable for this result.')

    st.markdown('<div style="height:.8rem"></div>', unsafe_allow_html=True)
    # st.markdown(
    #     '<div class="sec-label">Export Clinical Report</div>',
    #     unsafe_allow_html=True
    # )

    if not REPORTLAB_AVAILABLE:
        st.warning(
            'Install reportlab to enable PDF export:  '
            '`pip install reportlab`'
        )
    else:
        export_col1, export_col2 = st.columns([2, 1])
        with export_col1:
            st.caption(
                'Download a formatted PDF containing the patient data, '
                'risk result, SHAP explanation, and model information.'
            )
        with export_col2:
            shap_fig_stored = st.session_state.get('shap_fig')
            pdf_bytes = generate_pdf_report(
                age=inputs.age, gender=inputs.gender, sys_bp=inputs.sys_bp, dia_bp=inputs.dia_bp,
                chol=inputs.chol, gluc=inputs.gluc, bmi=inputs.bmi, smoking=inputs.smoking,
                alcohol=inputs.alcohol, active=inputs.active,
                prob=result['prob'],
                label=risk_tier(result['prob']),
                shap_fig=shap_fig_stored
            )
            st.download_button(
                label='Download report (PDF)',
                data=pdf_bytes,
                file_name=f"stroke_risk_{datetime.now():%Y%m%d_%H%M}.pdf",
                mime='application/pdf',
                width='stretch'
            )
