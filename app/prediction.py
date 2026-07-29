from datetime import datetime

import pandas as pd
import streamlit as st

from constants import PatientInputs, risk_tier
from model import model, explainer, features


def run_prediction(inputs: PatientInputs) -> None:
    """Compute the risk prediction + SHAP values and stash them into
    session_state, together with a snapshot of the inputs that produced
    them (so the result panel can detect staleness) and an appended session
    audit history entry. Call only when 'Run risk assessment' is pressed.
    """
    with st.spinner('Computing risk assessment…'):
        # Column order must match feature_names.pkl exactly — never change this.
        row = pd.DataFrame(
            [[inputs.age, inputs.gender, inputs.sys_bp, inputs.dia_bp,
              inputs.chol, inputs.gluc, inputs.smoking, inputs.alcohol,
              inputs.active, inputs.bmi]],
            columns=features
        )
        prob = float(model.predict_proba(row)[0][1])
        sv   = explainer.shap_values(row)
        st.session_state['result'] = {
            'prob': prob,
            'shap_values': sv[0],
            'base_value': explainer.expected_value,
            'data': row.values[0],
        }
        st.session_state['result_inputs'] = inputs

        # ── Append to session audit history ──────────────────────────────────
        if 'history' not in st.session_state:
            st.session_state['history'] = []

        tier = risk_tier(prob)
        st.session_state['history'].append({
            'Time':     datetime.now().strftime('%H:%M:%S'),
            'Age':      inputs.age,
            'Sys BP':   inputs.sys_bp,
            'BMI':      round(inputs.bmi, 1),
            'Risk (%)': round(prob * 100, 1),
            'Tier':     tier,
        })
        # Keep last 10 entries only
        st.session_state['history'] = st.session_state['history'][-10:]
