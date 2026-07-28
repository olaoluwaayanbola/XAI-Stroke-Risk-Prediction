from __future__ import annotations

import streamlit as st

from constants import GENDER_LABELS, LAB_LEVELS, YES_NO, ACTIVITY, PatientInputs


def render_summary_and_results(inputs: PatientInputs, result: dict | None, stale: bool) -> None:
    """Two-column section: live Patient Summary card (left) and the
    Risk Assessment result card / stale banner / empty-state prompt (right).
    """
    col_summary, col_res = st.columns([1, 1.2], gap='large')

    # ---- Patient summary panel ------------------------------------------------ #
    with col_summary:
        st.markdown('<div class="sec-label">Patient Summary</div>', unsafe_allow_html=True)
        st.markdown(
            f"""
            <div class="summary-card">
                <div class="summary-row"><span class="k">Age</span><span class="v">{inputs.age} yrs</span></div>
                <div class="summary-row"><span class="k">Gender</span><span class="v">{GENDER_LABELS[inputs.gender]}</span></div>
                <div class="summary-row"><span class="k">Blood pressure</span><span class="v">{inputs.sys_bp}/{inputs.dia_bp} mmHg</span></div>
                <div class="summary-row"><span class="k">Cholesterol</span><span class="v">{LAB_LEVELS[inputs.chol]}</span></div>
                <div class="summary-row"><span class="k">Glucose</span><span class="v">{LAB_LEVELS[inputs.gluc]}</span></div>
                <div class="summary-row"><span class="k">BMI</span><span class="v">{inputs.bmi:.1f}</span></div>
                <div class="summary-row"><span class="k">Smoking</span><span class="v">{YES_NO[inputs.smoking]}</span></div>
                <div class="summary-row"><span class="k">Alcohol</span><span class="v">{YES_NO[inputs.alcohol]}</span></div>
                <div class="summary-row"><span class="k">Physical activity</span><span class="v">{ACTIVITY[inputs.active]}</span></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ---- Results panel -------------------------------------------------------- #
    with col_res:
        st.markdown('<div class="sec-label">Risk Assessment</div>', unsafe_allow_html=True)

        if result is not None:
            if stale:
                st.markdown(
                    '<div class="stale-banner">Patient data changed since this result was computed — '
                    'click <strong>Run risk assessment</strong> to refresh.</div>',
                    unsafe_allow_html=True,
                )

            prob = result['prob']
            if prob >= 0.70:
                klass, label = 'high', 'High Risk'
            elif prob >= 0.40:
                klass, label = 'moderate', 'Moderate Risk'
            else:
                klass, label = 'low', 'Low Risk'

            st.markdown(
                f"""
                <div class="result-card {klass}">
                    <div style="font-size:.78rem;text-transform:uppercase;letter-spacing:.14em;color:#8a8577;">
                        Estimated CVD Risk Probability
                    </div>
                    <div class="result-prob {klass}">{prob:.1%}</div>
                    <div class="result-label {klass}">{label}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.markdown("<div style='height:.6rem'></div>", unsafe_allow_html=True)
            # st.progress(min(max(prob, 0.0), 1.0))
            st.caption('Risk thresholds: Low < 40% · Moderate 40–69% · High ≥ 70%')
        else:
            st.info('Review the patient summary on the left and select **Run risk assessment** to generate results.')
