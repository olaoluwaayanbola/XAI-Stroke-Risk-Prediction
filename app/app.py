from pathlib import Path

import streamlit as st
import joblib
import pandas as pd
import shap
import matplotlib.pyplot as plt

# Resolve paths relative to this script so it runs regardless of the launch directory
APP_DIR = Path(__file__).parent
ASSETS_DIR = APP_DIR / 'assets'

# Load saved model files from Colab
model     = joblib.load(APP_DIR / 'cardio_model.pkl')
scaler    = joblib.load(APP_DIR / 'cardio_scaler.pkl')
features  = joblib.load(APP_DIR / 'feature_names.pkl')
# Built locally instead of unpickling shap_explainer.pkl: SHAP's TreeExplainer
# embeds numba-JIT code objects whose pickle format isn't compatible across
# Python versions (the file was saved from a different Python than this machine runs).
explainer = shap.TreeExplainer(model)

# --------------------------------------------------------------------------- #
# Page configuration
# --------------------------------------------------------------------------- #
st.set_page_config(
    page_title='Stroke / CVD Risk — Clinical Decision Support',
    page_icon='🫀',
    layout='wide',
)

# --------------------------------------------------------------------------- #
# Academic theme (serif type, muted palette, journal-style layout)
# --------------------------------------------------------------------------- #
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,400;0,600;0,700;1,400&family=Source+Sans+3:wght@400;600&display=swap');

    html, body, [class*="css"]  { font-family: 'Source Sans 3', sans-serif; }

    /* Widen the reading column slightly and set a paper-like background */
    .stApp { background: #fbfaf7; }
    .block-container { padding-top: 2.2rem; max-width: 1150px; }

    /* Masthead ---------------------------------------------------------- */
    .masthead {
        border-top: 3px solid #2c3e50;
        border-bottom: 1px solid #cfc9bd;
        padding: 1.1rem 0 1.0rem 0;
        margin-bottom: 1.6rem;
        text-align: center;
    }
    .masthead .eyebrow {
        font-family: 'Source Sans 3', sans-serif;
        text-transform: uppercase;
        letter-spacing: .22em;
        font-size: .72rem;
        color: #8a8577;
        margin-bottom: .35rem;
    }
    .masthead h1 {
        font-family: 'Lora', serif;
        font-weight: 700;
        color: #1f2b38;
        font-size: 2.15rem;
        line-height: 1.15;
        margin: 0;
    }
    .masthead .subtitle {
        font-family: 'Lora', serif;
        font-style: italic;
        color: #5c6672;
        font-size: 1.02rem;
        margin-top: .45rem;
    }

    /* Section headings -------------------------------------------------- */
    h2, h3 { font-family: 'Lora', serif !important; color: #22303c !important; }
    .sec-label {
        font-family: 'Source Sans 3', sans-serif;
        text-transform: uppercase;
        letter-spacing: .16em;
        font-size: .74rem;
        font-weight: 600;
        color: #7a8794;
        border-bottom: 1px solid #e3ddd0;
        padding-bottom: .35rem;
        margin: .2rem 0 .9rem 0;
    }

    /* Figure / image panel --------------------------------------------- */
    .figure-frame {
        border: 1px solid #d9d3c6;
        background: #ffffff;
        padding: .55rem;
        border-radius: 3px;
        box-shadow: 0 1px 3px rgba(40,35,20,.06);
    }
    .figure-caption {
        font-family: 'Lora', serif;
        font-style: italic;
        font-size: .85rem;
        color: #6a7078;
        margin-top: .5rem;
        text-align: center;
    }
    .placeholder {
        border: 1px dashed #c4bdac;
        background: #f4f1ea;
        border-radius: 3px;
        min-height: 230px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #9a9384;
        font-family: 'Lora', serif;
        font-style: italic;
        text-align: center;
        padding: 1rem;
    }

    /* Result card ------------------------------------------------------- */
    .result-card {
        border: 1px solid #d9d3c6;
        border-left: 5px solid #2c3e50;
        background: #ffffff;
        padding: 1.1rem 1.3rem;
        border-radius: 3px;
    }
    .result-card.high { border-left-color: #9b2c2c; }
    .result-card.low  { border-left-color: #2f6b46; }
    .result-prob { font-family:'Lora',serif; font-size:2.6rem; font-weight:700; line-height:1; }
    .result-prob.high { color:#9b2c2c; }
    .result-prob.low  { color:#2f6b46; }
    .result-label {
        text-transform: uppercase; letter-spacing:.14em; font-size:.8rem;
        font-weight:600; margin-top:.35rem;
    }
    .result-label.high { color:#9b2c2c; }
    .result-label.low  { color:#2f6b46; }

    /* Sidebar ----------------------------------------------------------- */
    section[data-testid="stSidebar"] { background:#f2efe8; border-right:1px solid #ddd6c8; }
    section[data-testid="stSidebar"] h2 { font-family:'Lora',serif !important; }

    footer, #MainMenu { visibility: hidden; }
    .app-footer {
        margin-top: 2.5rem; padding-top: 1rem;
        border-top: 1px solid #e3ddd0;
        font-size: .8rem; color: #9a9384; text-align:center;
        font-family: 'Source Sans 3', sans-serif;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --------------------------------------------------------------------------- #
# Masthead — drop a logo at app/assets/logo.png to have it appear here
# --------------------------------------------------------------------------- #
logo = ASSETS_DIR / 'logo.png'
if logo.exists():
    lc1, lc2, lc3 = st.columns([1, 1, 1])
    with lc2:
        st.image(str(logo), use_container_width=True)

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

# --------------------------------------------------------------------------- #
# Sidebar — patient data entry
# --------------------------------------------------------------------------- #
with st.sidebar:
    st.header('Patient Data')
    st.caption('Enter the measurements below and run the assessment.')

    age        = st.number_input('Age (years)', 18, 90, 55)
    gender     = st.selectbox('Gender', [1, 2], format_func=lambda x: 'Female' if x == 1 else 'Male')
    sys_bp     = st.number_input('Systolic BP (mmHg)', 60, 250, 130)
    dia_bp     = st.number_input('Diastolic BP (mmHg)', 40, 150, 85)
    chol       = st.selectbox('Cholesterol', [1, 2, 3], format_func=lambda x: ['Normal', 'Above Normal', 'Well Above'][x - 1])
    gluc       = st.selectbox('Glucose', [1, 2, 3], format_func=lambda x: ['Normal', 'Above Normal', 'Well Above'][x - 1])
    bmi        = st.number_input('BMI', 10.0, 60.0, 25.0)
    smoking    = st.selectbox('Smoking', [0, 1], format_func=lambda x: 'No' if x == 0 else 'Yes')
    alcohol    = st.selectbox('Alcohol', [0, 1], format_func=lambda x: 'No' if x == 0 else 'Yes')
    active     = st.selectbox('Physical activity', [1, 0], format_func=lambda x: 'Active' if x == 1 else 'Not active')

    st.divider()
    predict_btn = st.button('Run risk assessment', type='primary', use_container_width=True)

# --------------------------------------------------------------------------- #
# Main body — two columns: imaging panel (left) and results (right)
# --------------------------------------------------------------------------- #
col_img, col_res = st.columns([1, 1.25], gap='large')

# ---- Image / figure panel ------------------------------------------------- #
with col_img:
    st.markdown('<div class="sec-label">Figure 1 — Patient Imaging</div>', unsafe_allow_html=True)

    uploaded = st.file_uploader(
        'Attach a scan or clinical image (PNG / JPG)',
        type=['png', 'jpg', 'jpeg'],
        help='Optional. Displayed alongside the risk assessment for reference.',
    )

    default_fig = ASSETS_DIR / 'sample_scan.png'
    if uploaded is not None:
        st.markdown('<div class="figure-frame">', unsafe_allow_html=True)
        st.image(uploaded, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('<div class="figure-caption">Figure 1. Uploaded patient image.</div>', unsafe_allow_html=True)
    elif default_fig.exists():
        st.markdown('<div class="figure-frame">', unsafe_allow_html=True)
        st.image(str(default_fig), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('<div class="figure-caption">Figure 1. Reference image.</div>', unsafe_allow_html=True)
    else:
        st.markdown(
            '<div class="placeholder">No image attached.<br>'
            'Upload a scan above, or place a file at<br><code>app/assets/sample_scan.png</code>.</div>',
            unsafe_allow_html=True,
        )

# On click, compute the prediction once and stash it so results persist across
# reruns triggered by other widgets (e.g. uploading an image).
if predict_btn:
    row  = pd.DataFrame([[age, gender, sys_bp, dia_bp, chol, gluc, smoking, alcohol, active, bmi]], columns=features)
    prob = float(model.predict_proba(row)[0][1])
    sv   = explainer.shap_values(row)
    st.session_state['result'] = {
        'prob': prob,
        'shap_values': sv[0],
        'base_value': explainer.expected_value,
        'data': row.values[0],
    }

result = st.session_state.get('result')

# ---- Results panel -------------------------------------------------------- #
with col_res:
    st.markdown('<div class="sec-label">Risk Assessment</div>', unsafe_allow_html=True)

    if result is not None:
        prob  = result['prob']
        high  = prob > 0.5
        klass = 'high' if high else 'low'
        label = 'High Risk' if high else 'Low Risk'

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
        st.progress(min(max(prob, 0.0), 1.0))
        st.caption('Decision threshold: 50%. Values above the threshold are flagged as high risk.')
    else:
        st.info('Enter patient data in the left panel and select **Run risk assessment** to generate results.')

# --------------------------------------------------------------------------- #
# Explanation section — the XAI layer (full width, below)
# --------------------------------------------------------------------------- #
if result is not None:
    st.markdown('<div style="height:1.4rem"></div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-label">Figure 2 — Why? Model Explanation (SHAP)</div>', unsafe_allow_html=True)
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
    shap.plots.waterfall(exp, show=False)
    fig = plt.gcf()
    fig.patch.set_facecolor('#fbfaf7')
    st.pyplot(fig, clear_figure=True)
    st.markdown(
        '<div class="figure-caption">Figure 2. Per-feature SHAP contributions to the individual risk estimate.</div>',
        unsafe_allow_html=True,
    )

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
