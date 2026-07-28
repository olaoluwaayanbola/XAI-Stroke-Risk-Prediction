from __future__ import annotations

import streamlit as st

from constants import GENDER_LABELS, LAB_LEVELS, YES_NO, ACTIVITY, PatientInputs


def render_sidebar() -> tuple[PatientInputs, bool]:
    """Render the patient-data entry form and the Clinical Flags card.
    Returns the collected inputs and whether 'Run risk assessment' was pressed
    (forced False if the BP contradiction check blocks the assessment).
    """
    with st.sidebar:
        st.header('Patient Data')
        st.caption('Enter the measurements below and run the assessment.')
        st.divider()

        st.markdown('<div class="field-group-label">Demographics</div>', unsafe_allow_html=True)
        age        = st.number_input('Age (years)', 18, 90, 55)
        gender     = st.selectbox('Gender', list(GENDER_LABELS), format_func=GENDER_LABELS.get)

        st.markdown('<div class="field-group-label">Vitals &amp; Labs</div>', unsafe_allow_html=True)
        sys_bp     = st.number_input('Systolic BP (mmHg)', 60, 250, 130)
        dia_bp     = st.number_input('Diastolic BP (mmHg)', 40, 150, 85)
        chol       = st.selectbox('Cholesterol', list(LAB_LEVELS), format_func=LAB_LEVELS.get)
        gluc       = st.selectbox('Glucose', list(LAB_LEVELS), format_func=LAB_LEVELS.get)
        bmi        = st.number_input('BMI', 10.0, 60.0, 25.0)

        st.markdown('<div class="field-group-label">Lifestyle</div>', unsafe_allow_html=True)
        smoking    = st.selectbox('Smoking', list(YES_NO), format_func=YES_NO.get)
        alcohol    = st.selectbox('Alcohol', list(YES_NO), format_func=YES_NO.get)
        active     = st.selectbox('Physical activity', list(ACTIVITY), format_func=ACTIVITY.get)

        st.divider()
        predict_btn = st.button('Run risk assessment', type='primary', use_container_width=True)

        st.divider()
        st.markdown(
            '<div class="field-group-label">Clinical Flags</div>',
            unsafe_allow_html=True
        )

        # ── Blood pressure + BMI flags, rendered as one compact card ──────────
        flags = []
        if sys_bp >= 180:
            flags.append(('high', 'Stage 3 hypertension', 'Urgent review indicated'))
        elif sys_bp >= 140:
            flags.append(('high', 'Stage 2 hypertension', 'Significantly elevated'))
        elif sys_bp >= 130:
            flags.append(('moderate', 'Stage 1 hypertension', 'Monitor closely'))
        else:
            flags.append(('low', 'Systolic BP', 'Within normal range'))

        if bmi >= 30:
            flags.append(('high', 'Obese', 'BMI ≥ 30 — increased CVD risk'))
        elif bmi >= 25:
            flags.append(('moderate', 'Overweight', 'BMI 25–29.9'))
        else:
            flags.append(('low', 'BMI', 'Within healthy range'))

        flag_rows = ''.join(
            f'<div class="flag-row {sev}"><span class="flag-dot"></span>'
            f'<div><span class="flag-title">{title}</span>'
            f'<span class="flag-detail">{detail}</span></div></div>'
            for sev, title, detail in flags
        )
        st.markdown(f'<div class="flag-card">{flag_rows}</div>', unsafe_allow_html=True)

        # ── BP contradiction check ────────────────────────────────────────────
        if sys_bp <= dia_bp:
            st.markdown(
                '<div class="alert-banner error">Systolic BP must exceed diastolic '
                'BP — check values.</div>',
                unsafe_allow_html=True
            )
            predict_btn = False   # block the assessment

        # ── Modifiable lifestyle risk count ──────────────────────────────────
        lifestyle_risks = sum([smoking == 1, alcohol == 1, active == 0])
        if lifestyle_risks >= 2:
            st.markdown(
                f'<div class="alert-banner warning">{lifestyle_risks}/3 modifiable '
                'lifestyle risk factors present. Behavioural intervention may '
                'reduce risk.</div>',
                unsafe_allow_html=True
            )

    inputs = PatientInputs(
        age=age, gender=gender, sys_bp=sys_bp, dia_bp=dia_bp,
        chol=chol, gluc=gluc, bmi=bmi,
        smoking=smoking, alcohol=alcohol, active=active,
    )
    return inputs, predict_btn


def render_session_history() -> None:
    """Session History list, appended to the sidebar. Rendered in its own
    `with st.sidebar:` block *after* prediction.run_prediction() has run, so
    it reflects this rerun's history entry immediately — render_sidebar()
    above executes before the predict_btn history append, so reading
    session_state['history'] there would always show last run's data.
    """
    if not st.session_state.get('history'):
        return

    with st.sidebar:
        st.divider()
        st.markdown(
            '<div class="field-group-label">Session History</div>',
            unsafe_allow_html=True
        )
        for entry in reversed(st.session_state['history']):
            c = (
                '#9b2c2c' if entry['Tier'] == 'High'     else
                '#92400e' if entry['Tier'] == 'Moderate' else
                '#2f6b46'
            )
            st.markdown(
                f"<div style='font-size:.78rem;line-height:1.7'>"
                f"<span style='color:{c};font-weight:600'>{entry['Tier']}</span>"
                f"&nbsp;{entry['Risk (%)']:.1f}%"
                f"&nbsp;·&nbsp;Age {entry['Age']}"
                f"&nbsp;·&nbsp;BP {entry['Sys BP']}"
                f"&nbsp;·&nbsp;"
                f"<span style='color:#8a8577'>{entry['Time']}</span>"
                f"</div>",
                unsafe_allow_html=True
            )
