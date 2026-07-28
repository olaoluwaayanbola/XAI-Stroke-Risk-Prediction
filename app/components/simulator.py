from __future__ import annotations

import pandas as pd
import streamlit as st

from constants import ACTIVITY, PatientInputs
from model import model, features


def render_simulator(inputs: PatientInputs, result: dict | None) -> None:
    """What-If Intervention Simulator expander. No-op until a prediction has
    been run.
    """
    if result is None:
        return

    st.markdown('<div style="height:1rem"></div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sec-label">What-If Intervention Simulator</div>',
        unsafe_allow_html=True
    )
    st.write(
        'Adjust modifiable risk factors below to project how clinical '
        'interventions might change this patient\'s estimated risk. '
        'All other values remain as entered.'
    )

    with st.expander('Open simulator', expanded=False):

        sim_c1, sim_c2, sim_c3 = st.columns(3)

        with sim_c1:
            sim_bp = st.slider(
                'Systolic BP (mmHg)',
                min_value=60, max_value=250,
                value=int(inputs.sys_bp), step=1,
                key='sim_bp'
            )
        with sim_c2:
            sim_bmi = st.slider(
                'BMI (kg/m²)',
                min_value=10.0, max_value=60.0,
                value=float(inputs.bmi), step=0.5,
                key='sim_bmi'
            )
        with sim_c3:
            sim_active = st.selectbox(
                'Physical activity',
                list(ACTIVITY),
                format_func=ACTIVITY.get,
                key='sim_active'
            )

        # Counterfactual prediction — same column order as the main prediction
        sim_row = pd.DataFrame(
            [[inputs.age, inputs.gender, sim_bp, inputs.dia_bp, inputs.chol, inputs.gluc,
              inputs.smoking, inputs.alcohol, sim_active, sim_bmi]],
            columns=features
        )
        sim_prob = float(model.predict_proba(sim_row)[0][1])
        delta    = sim_prob - result['prob']

        st.metric(
            label='Projected risk with interventions',
            value=f'{sim_prob:.1%}',
            delta=f'{delta:+.1%}',
            delta_color='inverse'   # green for decrease, red for increase
        )

        if delta <= -0.05:
            st.success(
                f'These changes project a risk reduction of {abs(delta):.1%}. '
                'Consider discussing these interventions with the patient.'
            )
        elif delta < 0:
            st.info(f'Modest projected risk reduction of {abs(delta):.1%}.')
        elif delta == 0.0:
            st.info('No change projected with these settings.')
        else:
            st.warning(f'These settings project an increase of {delta:.1%}.')

        st.caption(
            'This simulator projects the model\'s response to input changes only. '
            'It does not account for pharmacological effects, patient adherence, '
            'or comorbidities. Results are illustrative, not prescriptive.'
        )
