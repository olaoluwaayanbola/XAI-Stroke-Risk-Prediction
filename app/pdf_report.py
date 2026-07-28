import io
from datetime import datetime

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.lib.colors import HexColor
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table,
        TableStyle, Image as RLImage, HRFlowable, KeepTogether
    )
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

from constants import GENDER_LABELS, LAB_LEVELS, YES_NO, ACTIVITY


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
    risk_style     = S('Normal',   fontSize=28, leading=34, textColor=risk_colour,
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
    story.append(Spacer(1, 10))

    # ── Section 2: Risk result ────────────────────────────────────────────
    story.append(HRFlowable(width='100%', thickness=0.5, color=C_BORDER, spaceAfter=8))
    story.append(Paragraph('Risk Assessment Result', section_style))
    story.append(Paragraph(f'{prob:.1%}', risk_style))
    story.append(Paragraph(label.upper(), S('Normal', fontSize=11,
        textColor=risk_colour, fontName='Helvetica-Bold', spaceAfter=4)))
    story.append(Paragraph(
        'Risk thresholds: Low &lt; 40% · Moderate 40–69% · High ≥ 70%',
        small_style))
    story.append(Spacer(1, 10))

    # ── Section 3: SHAP figure ────────────────────────────────────────────
    # Grouped with KeepTogether so the heading never gets orphaned on one
    # page while the (much taller) image flows to the next.
    if shap_fig is not None:
        img_buf = io.BytesIO()
        shap_fig.savefig(img_buf, format='png', dpi=150,
                         bbox_inches='tight', facecolor='#fbfaf7')
        img_buf.seek(0)
        story.append(KeepTogether([
            HRFlowable(width='100%', thickness=0.5, color=C_BORDER, spaceAfter=8),
            Paragraph('Model Explanation (SHAP)', section_style),
            RLImage(img_buf, width=15*cm, height=7*cm),
            Paragraph(
                'Figure 1. Per-feature SHAP contributions to the individual risk estimate. '
                'Red bars increase risk; blue bars decrease it.',
                small_style),
        ]))
        story.append(Spacer(1, 10))

    # ── Section 4: Model information ──────────────────────────────────────
    story.append(HRFlowable(width='100%', thickness=0.5, color=C_BORDER, spaceAfter=8))
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
