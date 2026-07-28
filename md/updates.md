ALREADY IN THE APP ✅ ─ GENDER_LABELS, LAB_LEVELS, YES_NO, ACTIVITY dicts (single source of truth) ─ model, scaler, features, explainer loaded at top ─ st.set_page_config with wide layout ─ Full CSS block including: masthead, sec-label, figure-frame, figure-caption, placeholder, result-card (high/low), summary-card, summary-row, stale-banner, field-group-label, sidebar, app-footer ─ Logo loader (ASSETS_DIR / 'logo.png') ─ Masthead HTML block ─ Sidebar with Demographics / Vitals & Labs / Lifestyle groups Variables: age, gender, sys_bp, dia_bp, chol, gluc, bmi, smoking, alcohol, active ← DO NOT RENAME THESE ─ current_inputs tuple for stale detection ─ predict_btn → st.spinner → session_state['result'] + ['result_inputs'] ─ col_summary (Patient Summary card, left column) ─ col_res (Risk Assessment, right column) with stale-banner ─ Binary risk logic: high = prob > 0.5 ← Phase 1 fixes this ─ SHAP waterfall as Figure 1 (full width, below columns) ─ App footer

NOT YET IN THE APP ❌ ← these are what the phases below add ─ Three-tier risk (Low / Moderate / High at 0.40 / 0.70 thresholds) ─ Moderate CSS class ─ Live clinical flags in sidebar ─ What-if intervention simulator ─ PDF report export ─ LIME validation ─ Model Trust Dashboard ─ Session prediction history ─ CSV audit log

THE FEATURE → DATAFRAME MAPPING (never change this): pd.DataFrame([[age, gender, sys_bp, dia_bp, chol, gluc, smoking, alcohol, active, bmi]], columns=features) features = ['age','gender','systolic_bp','diastolic_bp', 'cholesterol_level','glucose_level','smoking', 'alcohol_intake','physical_activity','bmi']

COLOURS (use exactly — already established in the theme): Background: 
#fbfaf7 Sidebar bg: 
#f2efe8 Primary text: 
#1f2b38 Border: 
#e3ddd0 / 
#d9d3c6 Secondary text: 
#5c6672 Card bg: 
#ffffff Muted: 
#8a8577 Accent: 
#2c3e50 High risk red: 
#9b2c2c Low risk green: 
#2f6b46 Moderate amber: 
#92400e ← NEW, add in Phase 1 Stale amber: 
#7a5c17 (text) / 
#fbf3de (bg) / 
#e0c891 (border) Font serif: 'Lora', serif Font sans: 'Source Sans 3', sans-serif

MODEL METRICS (for Model Trust Dashboard): Gradient Boosting → AUC:0.7999 Recall:0.6942 Precision:0.7468 F1:0.7195 XGBoost (deployed)→ AUC:0.7949 Recall:0.6817 Precision:0.7468 F1:0.7128 Logistic Regression→ AUC:0.7903 Recall:0.6673 Precision:0.7478 F1:0.7052 Random Forest → AUC:0.7595 Recall:0.6939 Precision:0.6972 F1:0.6956 Dataset: 68,608 patients · 49.5% CVD · 50.5% non-CVD (Ulianova, Kaggle 2019)

══════════════════════════════════════════════════════════════════════════════ PHASE 1 — Three-tier risk + live clinical flags in sidebar ══════════════════════════════════════════════════════════════════════════════

TASK 1A — Fix risk tiers (3 changes, all in one place) ────────────────────────────────────────────────────────

Change 1: In the CSS <style> block, add three new classes AFTER the existing .result-label.low rule:

.result-card.moderate  { border-left-color: #92400e; }
.result-prob.moderate  { color: #92400e; }
.result-label.moderate { color: #92400e; }

Change 2: In the col_res block, replace the binary risk logic:

REMOVE: high = prob > 0.5 klass = 'high' if high else 'low' label = 'High Risk' if high else 'Low Risk'

REPLACE WITH: if prob >= 0.70: klass, label = 'high', 'High Risk' elif prob >= 0.40: klass, label = 'moderate', 'Moderate Risk' else: klass, label = 'low', 'Low Risk'

Change 3: Update the caption under st.progress():

REMOVE: st.caption('Decision threshold: 50%. Values above the threshold are flagged as high risk.')

REPLACE WITH: st.caption('Risk thresholds: Low < 40% · Moderate 40–69% · High ≥ 70%')

Also add a helper function just before the col_summary/col_res block (needed by Phase 5 history — add it now so Phase 5 can use it):

def risk_tier(p: float) -> str:
    """Return 'High', 'Moderate', or 'Low' for a given probability."""
    if p >= 0.70: return 'High'
    if p >= 0.40: return 'Moderate'
    return 'Low'

TASK 1B — Live clinical flags in sidebar ───────────────────────────────────────── In the sidebar with block, AFTER the predict_btn line and BEFORE the closing of the with st.sidebar block, add:

st.divider()
st.markdown(
    '<div class="field-group-label">Clinical Flags</div>',
    unsafe_allow_html=True
)

# ── Blood pressure flag ──────────────────────────────────────────────
if sys_bp >= 180:
    st.markdown(
        '🔴 **Stage 3 hypertension** — urgent review indicated',
        unsafe_allow_html=False
    )
elif sys_bp >= 140:
    st.markdown('🟠 **Stage 2 hypertension** — significantly elevated')
elif sys_bp >= 130:
    st.markdown('🟡 **Stage 1 hypertension** — monitor closely')
else:
    st.markdown('🟢 Systolic BP within normal range')

# ── BMI flag ─────────────────────────────────────────────────────────
if bmi >= 30:
    st.markdown('🟠 **Obese** (BMI ≥ 30) — increased CVD risk')
elif bmi >= 25:
    st.markdown('🟡 **Overweight** (BMI 25–29.9)')
else:
    st.markdown('🟢 BMI within healthy range')

# ── BP contradiction check ────────────────────────────────────────────
if sys_bp <= dia_bp:
    st.error('⚠ Systolic BP must exceed diastolic BP — check values.')
    predict_btn = False   # block the assessment

# ── Modifiable lifestyle risk count ──────────────────────────────────
lifestyle_risks = sum([smoking == 1, alcohol == 1, active == 0])
if lifestyle_risks >= 2:
    st.warning(
        f'{lifestyle_risks}/3 modifiable lifestyle risk factors present. '
        'Behavioural intervention may reduce risk.'
    )

══════════════════════════════════════════════════════════════════════════════ PHASE 2 — What-if intervention simulator ══════════════════════════════════════════════════════════════════════════════

Location: add this AFTER the SHAP section (after the figure-caption div) and BEFORE the footer. It only renders when result is not None.

if result is not None:

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
                value=int(sys_bp), step=1,
                key='sim_bp'
            )
        with sim_c2:
            sim_bmi = st.slider(
                'BMI (kg/m²)',
                min_value=10.0, max_value=60.0,
                value=float(bmi), step=0.5,
                key='sim_bmi'
            )
        with sim_c3:
            sim_active = st.selectbox(
                'Physical activity',
                list(ACTIVITY),
                format_func=ACTIVITY.get,
                key='sim_active'
            )

        # Counterfactual prediction — same mapping as the main prediction
        sim_row  = pd.DataFrame(
            [[age, gender, sim_bp, dia_bp, chol, gluc,
              smoking, alcohol, sim_active, sim_bmi]],
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

══════════════════════════════════════════════════════════════════════════════ PHASE 3 — PDF clinical report export ══════════════════════════════════════════════════════════════════════════════

STEP 1: Add imports at the top of app.py, after the existing imports:

import io
from datetime import datetime

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.lib.colors import HexColor
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table,
        TableStyle, Image as RLImage, HRFlowable
    )
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

STEP 2: Define generate_pdf_report() as a module-level function AFTER the imports and label-dict definitions but BEFORE st.set_page_config.

Here is the complete function:

def generate_pdf_report(
    age, gender, sys_bp, dia_bp, chol, gluc, bmi,
    smoking, alcohol, active,
    prob: float, label: str, shap_fig
) -> bytes:
    """
    Build an A4 clinical risk report in memory and return raw PDF bytes.
    Never writes to disk — uses io.BytesIO throughout.
    """
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm
    )

    styles = getSampleStyleSheet()
    story  = []

    # ── Colours ──────────────────────────────────────────────────────────
    C_DARK    = HexColor('#1f2b38')
    C_MID     = HexColor('#5c6672')
    C_MUTED   = HexColor('#8a8577')
    C_BORDER  = HexColor('#d9d3c6')
    C_HIGH    = HexColor('#9b2c2c')
    C_MOD     = HexColor('#92400e')
    C_LOW     = HexColor('#2f6b46')
    C_BG      = HexColor('#fbfaf7')
    risk_colour = C_HIGH if prob >= 0.70 else (C_MOD if prob >= 0.40 else C_LOW)

    # ── Style definitions ─────────────────────────────────────────────────
    def S(name, **kw):
        s = styles[name].clone(name + '_custom')
        for k, v in kw.items():
            setattr(s, k, v)
        return s

    title_style    = S('Heading1', fontSize=18, textColor=C_DARK,
                       fontName='Times-Bold', spaceAfter=4)
    subtitle_style = S('Normal',   fontSize=10, textColor=C_MID,
                       fontName='Times-Italic', spaceAfter=2)
    meta_style     = S('Normal',   fontSize=8,  textColor=C_MUTED,
                       fontName='Helvetica', spaceAfter=12)
    section_style  = S('Heading2', fontSize=10, textColor=C_DARK,
                       fontName='Helvetica-Bold', spaceBefore=14, spaceAfter=6,
                       textTransform='uppercase')
    body_style     = S('Normal',   fontSize=9,  textColor=C_DARK,
                       fontName='Helvetica', leading=14)
    small_style    = S('Normal',   fontSize=7.5, textColor=C_MUTED,
                       fontName='Helvetica-Oblique', leading=11)
    risk_style     = S('Normal',   fontSize=28, textColor=risk_colour,
                       fontName='Times-Bold', spaceAfter=2)

    # ── Header ────────────────────────────────────────────────────────────
    story.append(Paragraph('Stroke &amp; CVD Risk Assessment Report', title_style))
    story.append(Paragraph(
        'Explainable AI · Clinical Decision Support System', subtitle_style))
    story.append(Paragraph(
        f'Generated: {datetime.now():%d %B %Y, %H:%M}  '
        f'&nbsp;&nbsp;|&nbsp;&nbsp;  For clinical decision support only',
        meta_style))
    story.append(HRFlowable(width='100%', thickness=1,
                            color=C_BORDER, spaceAfter=12))

    # ── Section 1: Patient data ───────────────────────────────────────────
    story.append(Paragraph('Patient Data', section_style))

    patient_rows = [
        ['Parameter', 'Value'],
        ['Age',              f'{age} years'],
        ['Gender',           GENDER_LABELS[gender]],
        ['Systolic BP',      f'{sys_bp} mmHg'],
        ['Diastolic BP',     f'{dia_bp} mmHg'],
        ['Cholesterol',      LAB_LEVELS[chol]],
        ['Glucose',          LAB_LEVELS[gluc]],
        ['BMI',              f'{bmi:.1f} kg/m²'],
        ['Smoking',          YES_NO[smoking]],
        ['Alcohol intake',   YES_NO[alcohol]],
        ['Physical activity',ACTIVITY[active]],
    ]

    pt = Table(patient_rows, colWidths=[7*cm, 9*cm])
    pt.setStyle(TableStyle([
        ('FONTNAME',    (0,0), (-1,0),  'Helvetica-Bold'),
        ('FONTNAME',    (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE',    (0,0), (-1,-1),  9),
        ('TEXTCOLOR',   (0,0), (-1,0),  C_DARK),
        ('TEXTCOLOR',   (0,1), (0,-1),  C_MUTED),
        ('TEXTCOLOR',   (1,1), (1,-1),  C_DARK),
        ('BACKGROUND',  (0,0), (-1,0),  HexColor('#f2efe8')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [HexColor('#ffffff'), HexColor('#fbfaf7')]),
        ('GRID',        (0,0), (-1,-1), 0.4, C_BORDER),
        ('TOPPADDING',  (0,0), (-1,-1), 5),
        ('BOTTOMPADDING',(0,0),(-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 7),
    ]))
    story.append(pt)
    story.append(Spacer(1, 14))

    # ── Section 2: Risk result ────────────────────────────────────────────
    story.append(HRFlowable(width='100%', thickness=0.5, color=C_BORDER, spaceAfter=8))
    story.append(Paragraph('Risk Assessment Result', section_style))
    story.append(Paragraph(f'{prob:.1%}', risk_style))
    story.append(Paragraph(label.upper(), S('Normal', fontSize=11,
        textColor=risk_colour, fontName='Helvetica-Bold', spaceAfter=4)))
    story.append(Paragraph(
        'Risk thresholds: Low &lt; 40% · Moderate 40–69% · High ≥ 70%',
        small_style))
    story.append(Spacer(1, 14))

    # ── Section 3: SHAP figure ────────────────────────────────────────────
    if shap_fig is not None:
        story.append(HRFlowable(width='100%', thickness=0.5, color=C_BORDER, spaceAfter=8))
        story.append(Paragraph('Model Explanation (SHAP)', section_style))
        img_buf = io.BytesIO()
        shap_fig.savefig(img_buf, format='png', dpi=150,
                         bbox_inches='tight', facecolor='#fbfaf7')
        img_buf.seek(0)
        story.append(RLImage(img_buf, width=16*cm, height=8*cm))
        story.append(Paragraph(
            'Figure 1. Per-feature SHAP contributions to the individual risk estimate. '
            'Red bars increase risk; blue bars decrease it.',
            small_style))
        story.append(Spacer(1, 14))

    # ── Section 4: Disclaimer ─────────────────────────────────────────────
    story.append(HRFlowable(width='100%', thickness=0.5, color=C_BORDER, spaceAfter=8))
    story.append(Paragraph(
        'This report is generated by an AI-based research prototype and is '
        'intended for clinical decision support only. It must not be used as '
        'the sole basis for diagnosis or treatment. All findings should be '
        'reviewed by a qualified healthcare professional in conjunction with '
        'full clinical assessment.',
        small_style))
    story.append(Spacer(1, 8))

    # ── Section 5: Model information ──────────────────────────────────────
    story.append(Paragraph('Model Information', section_style))
    model_rows = [
        ['Algorithm',  'XGBoost (Extreme Gradient Boosting)'],
        ['Dataset',    'Cardiovascular Disease Dataset (Ulianova, Kaggle 2019)'],
        ['Training N', '68,608 patients'],
        ['AUC-ROC',   '0.7949 (test set)'],
        ['XAI method', 'SHAP TreeExplainer (exact Shapley values)'],
    ]
    mt = Table(model_rows, colWidths=[4*cm, 12*cm])
    mt.setStyle(TableStyle([
        ('FONTNAME',    (0,0), (0,-1),  'Helvetica-Bold'),
        ('FONTNAME',    (1,0), (1,-1),  'Helvetica'),
        ('FONTSIZE',    (0,0), (-1,-1),  8),
        ('TEXTCOLOR',   (0,0), (0,-1),  C_MUTED),
        ('TEXTCOLOR',   (1,0), (1,-1),  C_DARK),
        ('GRID',        (0,0), (-1,-1), 0.4, C_BORDER),
        ('TOPPADDING',  (0,0), (-1,-1), 4),
        ('BOTTOMPADDING',(0,0),(-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 7),
    ]))
    story.append(mt)

    doc.build(story)
    buf.seek(0)
    return buf.read()

STEP 3: In the SHAP section, change clear_figure=True to clear_figure=False and store the fig in session_state:

CHANGE:
    st.pyplot(fig, clear_figure=True)

TO:
    st.pyplot(fig, clear_figure=False)
    st.session_state['shap_fig'] = fig

STEP 4: After the SHAP figure-caption div and BEFORE the what-if simulator section, add the export block:

st.markdown('<div style="height:.8rem"></div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sec-label">Export Clinical Report</div>',
    unsafe_allow_html=True
)

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
            age=age, gender=gender, sys_bp=sys_bp, dia_bp=dia_bp,
            chol=chol, gluc=gluc, bmi=bmi, smoking=smoking,
            alcohol=alcohol, active=active,
            prob=result['prob'],
            label=risk_tier(result['prob']),
            shap_fig=shap_fig_stored
        )
        st.download_button(
            label='Download report (PDF)',
            data=pdf_bytes,
            file_name=f"stroke_risk_{datetime.now():%Y%m%d_%H%M}.pdf",
            mime='application/pdf',
            use_container_width=True
        )

══════════════════════════════════════════════════════════════════════════════ PHASE 4 — LIME validation + Model Trust Dashboard ══════════════════════════════════════════════════════════════════════════════

TASK 4A: LIME — add import block after existing imports:

try:
    from lime.lime_tabular import LimeTabularExplainer
    LIME_AVAILABLE = True
except ImportError:
    LIME_AVAILABLE = False

import numpy as np   # add only if not already imported

TASK 4B: LIME panel — add after the what-if simulator section, still inside if result is not None:

st.markdown('<div style="height:.8rem"></div>', unsafe_allow_html=True)

with st.expander('LIME — Independent Explanation Validation',
                 expanded=False):

    st.write(
        'LIME (Local Interpretable Model-agnostic Explanations) validates '
        'the SHAP output using a mathematically independent method. '
        'When both methods agree on the dominant risk factors, clinical '
        'confidence in the explanation is substantially increased.'
    )

    if not LIME_AVAILABLE:
        st.warning('Install lime to enable this feature: `pip install lime`')

    else:
        if st.button('Generate LIME explanation', key='lime_btn'):

            with st.spinner('Running LIME perturbation analysis…'):

                # Synthetic training reference from feature ranges
                # (original training data is not shipped with the app)
                rng = np.random.default_rng(42)
                bounds = [
                    (18, 90), (1, 2), (60, 250), (40, 200),
                    (1, 3), (1, 3), (0, 1), (0, 1), (0, 1), (10, 60)
                ]
                training_ref = np.column_stack([
                    rng.uniform(lo, hi, 1000) for lo, hi in bounds
                ])

                lime_explainer = LimeTabularExplainer(
                    training_data=training_ref,
                    feature_names=features,
                    class_names=['No CVD', 'Has CVD'],
                    mode='classification',
                    random_state=42
                )

                lime_result = lime_explainer.explain_instance(
                    data_row=result['data'],
                    predict_fn=model.predict_proba,
                    num_features=10
                )
                st.session_state['lime_result']   = lime_result
                st.session_state['lime_fidelity'] = lime_result.score

        if 'lime_result' in st.session_state:

            lime_r   = st.session_state['lime_result']
            fidelity = st.session_state['lime_fidelity']

            lime_left, lime_right = st.columns([2.2, 1])

            with lime_left:
                lime_vals   = lime_r.as_list()
                feat_labels = [x[0] for x in lime_vals]
                feat_contr  = [x[1] for x in lime_vals]
                bar_colors  = ['#9b2c2c' if v > 0 else '#2f6b46'
                               for v in feat_contr]

                fig_lime, ax = plt.subplots(figsize=(7, 4))
                fig_lime.patch.set_facecolor('#fbfaf7')
                ax.set_facecolor('#fbfaf7')
                ax.barh(feat_labels, feat_contr,
                        color=bar_colors, height=0.55)
                ax.axvline(0, color='#cfc9bd', linewidth=0.8)
                ax.set_xlabel('Feature contribution',
                              fontsize=9, fontfamily='Source Sans 3')
                ax.spines[['top', 'right', 'left']].set_visible(False)
                ax.tick_params(labelsize=8)
                st.pyplot(fig_lime, clear_figure=True)
                st.markdown(
                    '<div class="figure-caption">Figure 2. LIME feature '
                    'contributions for this patient.</div>',
                    unsafe_allow_html=True
                )

            with lime_right:

                st.metric(
                    'Local Fidelity Score', f'{fidelity:.3f}',
                    help=(
                        'Measures how accurately the LIME surrogate model '
                        'approximates the black-box model in the local '
                        'neighbourhood of this patient. Score > 0.80 = '
                        'reliable; 0.60–0.80 = acceptable; < 0.60 = caution.'
                    )
                )

                if fidelity >= 0.80:
                    st.success('High fidelity — explanation is reliable.')
                elif fidelity >= 0.60:
                    st.warning('Moderate fidelity — interpret with caution.')
                else:
                    st.error('Low fidelity — explanation may not be reliable.')

                st.markdown('---')

                # SHAP vs LIME agreement check
                shap_top3 = set(
                    pd.Series(
                        abs(result['shap_values']),
                        index=features
                    ).nlargest(3).index
                )
                lime_top3 = set()
                for feat_str, _ in lime_r.as_list()[:3]:
                    for f in features:
                        if f in feat_str:
                            lime_top3.add(f)
                            break

                overlap = shap_top3 & lime_top3
                if len(overlap) >= 2:
                    st.success(
                        f' SHAP and LIME agree on **{len(overlap)}/3** '
                        f'top risk drivers  ({", ".join(sorted(overlap))}).\n\n'
                        'Cross-method agreement strengthens confidence in '
                        'the explanation.'
                    )
                else:
                    st.warning(
                        '⚠ SHAP and LIME highlight different top features. '
                        'Review both explanations independently before '
                        'drawing clinical conclusions.'
                    )

TASK 4C: Model Trust Dashboard — add inside the footer block, as a st.expander BEFORE the footer HTML div:

with st.expander('📊 Model Trust Dashboard', expanded=False):

    st.write(
        'This dashboard presents the validated performance of the '
        'deployed XGBoost model, evaluated on an independent held-out '
        'test set. It is intended to support informed, transparent '
        'use of the system by clinical staff.'
    )

    st.markdown(
        '<div class="sec-label">Deployed model — XGBoost</div>',
        unsafe_allow_html=True
    )

    m1, m2, m3, m4 = st.columns(4)
    m1.metric('AUC-ROC',   '0.7949',
              help='Area under the ROC curve — overall discriminative ability')
    m2.metric('Recall',    '0.6817',
              help='Sensitivity — proportion of true CVD cases correctly flagged')
    m3.metric('Precision', '0.7468',
              help='Positive predictive value — accuracy of high-risk flags')
    m4.metric('F1 Score',  '0.7128',
              help='Harmonic mean of Precision and Recall')

    st.divider()
    st.markdown(
        '<div class="sec-label">Comparative model performance</div>',
        unsafe_allow_html=True
    )

    perf_df = pd.DataFrame({
        'Model': [
            'Gradient Boosting ★',
            'XGBoost (deployed)',
            'Logistic Regression',
            'Random Forest'
        ],
        'AUC-ROC':   [0.7999, 0.7949, 0.7903, 0.7595],
        'Recall':    [0.6942, 0.6817, 0.6673, 0.6939],
        'Precision': [0.7468, 0.7468, 0.7478, 0.6972],
        'F1 Score':  [0.7195, 0.7128, 0.7052, 0.6956],
    })
    st.dataframe(perf_df, use_container_width=True, hide_index=True)
    st.caption(
        '★ Gradient Boosting achieved the highest AUC-ROC. XGBoost was '
        'selected for deployment because SHAP\'s TreeExplainer computes '
        'exact Shapley values for tree-based models — a requirement for '
        'rigorous XAI output. The marginal AUC difference (0.0050) does '
        'not constitute a clinically meaningful performance gap.'
    )

    st.divider()
    inf1, inf2, inf3 = st.columns(3)
    inf1.info(
        '**Dataset**  \nCardiovascular Disease Dataset  \n'
        'Ulianova, Kaggle 2019  \n68,608 patients'
    )
    inf2.info(
        '**XAI methods**  \n'
        'SHAP TreeExplainer (global + local)  \n'
        'LIME LimeTabularExplainer (local validation)'
    )
    inf3.info(
        '**Validation**  \n'
        '5-fold cross-validation  \n'
        'Independent held-out test set  \n'
        'APA 7th edition reporting'
    )

══════════════════════════════════════════════════════════════════════════════ PHASE 5 — Session history + CSV audit log ══════════════════════════════════════════════════════════════════════════════

TASK 5A: Append to session history inside the predict_btn block

In the if predict_btn: block, AFTER the session_state['result'] and session_state['result_inputs'] lines, add:

# ── Append to session audit history ──────────────────────────────────
if 'history' not in st.session_state:
    st.session_state['history'] = []

tier = risk_tier(prob)
tier_colour = (
    '#9b2c2c' if tier == 'High' else
    '#92400e' if tier == 'Moderate' else
    '#2f6b46'
)
st.session_state['history'].append({
    'Time':     datetime.now().strftime('%H:%M:%S'),
    'Age':      age,
    'Sys BP':   sys_bp,
    'BMI':      round(bmi, 1),
    'Risk (%)': round(prob * 100, 1),
    'Tier':     tier,
})
# Keep last 10 entries only
st.session_state['history'] = st.session_state['history'][-10:]

TASK 5B: Show history in sidebar

In the sidebar with block, AFTER the Clinical Flags section from Phase 1, add:

if st.session_state.get('history'):
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

TASK 5C: Add CSV audit log to the Model Trust Dashboard

Inside the with st.expander('📊 Model Trust Dashboard') block added in Phase 4, AFTER the three info columns, add:

st.divider()
st.markdown(
    '<div class="sec-label">Session Audit Log</div>',
    unsafe_allow_html=True
)

if st.session_state.get('history'):
    audit_df = pd.DataFrame(st.session_state['history'])
    st.dataframe(audit_df, use_container_width=True, hide_index=True)
    st.download_button(
        label='📥 Download audit log (CSV)',
        data=audit_df.to_csv(index=False).encode('utf-8'),
        file_name=f"cdss_audit_{datetime.now():%Y%m%d}.csv",
        mime='text/csv',
        help='Full record of all risk assessments run in this session'
    )
    st.caption(
        'This log supports clinical governance and audit requirements. '
        'Downloaded files are not transmitted — all processing is local.'
    )
else:
    st.info(
        'No assessments recorded yet in this session. '
        'Run a risk assessment to begin logging.'
    )

══════════════════════════════════════════════════════════════════════════════ IMPLEMENTATION RULES — NON-NEGOTIABLE ══════════════════════════════════════════════════════════════════════════════

Do NOT touch the model loading block, the label dicts, or the feature → DataFrame mapping. They are correct and must not change.
Do NOT add new CSS classes inside the existing <style> block — append them after the last existing rule, before the closing </style>.
PRESERVE the stale-result detection logic exactly: current_inputs = (age, gender, sys_bp, dia_bp, chol, gluc, bmi, smoking, alcohol, active) stale = result is not None and st.session_state.get('result_inputs') != current_inputs
ALL new matplotlib figures must set: fig.patch.set_facecolor('
#fbfaf7') ax.set_facecolor('
#fbfaf7')
Every new section heading uses the existing .sec-label class: st.markdown('<div class="sec-label">Title</div>', unsafe_allow_html=True)
Keep all new st.expander() calls defaulting to expanded=False.
British English in all user-facing strings: "Analyse" not "Analyze", "Behaviour" not "Behavior", "Recognised" not "Recognized", "Optimise" not "Optimize", "Judgement" not "Judgment".
The risk_tier() helper function is defined in Phase 1 — all subsequent phases depend on it. Never inline the threshold logic.
The datetime import (Phase 3) is needed by Phase 5 too — add it once at the top, reference it everywhere.
After every phase, output the COMPLETE updated app.py — not a diff, not a snippet — so it can be copied and run directly.

══════════════════════════════════════════════════════════════════════════════ BUILD ORDER + CONFIRMATION PROTOCOL ══════════════════════════════════════════════════════════════════════════════

Build exactly one phase at a time. After each phase: → Output the complete updated app.py → List changes made (3 bullet points max) → State: "Phase N complete. Type 'next' to continue to Phase N+1."

Wait for me to type "next" before starting the next phase.

If I type "skip", skip the current phase and move to the next. If I type "redo", redo the current phase from scratch.

Start with PHASE 1