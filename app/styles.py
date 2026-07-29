import streamlit as st

# Academic theme (serif type, muted palette, journal-style layout)
APP_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,400;0,600;0,700;1,400&family=Source+Sans+3:wght@400;600&display=swap');

html, body, [class*="css"]  { font-family: 'Source Sans 3', sans-serif; }

/* This design is light-only (no dark variant exists) — opt out of the
   browser's own automatic dark repainting (seen on some mobile browsers)
   so our explicit colors below are always what actually renders. */
:root { color-scheme: light only; }

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
.result-card.moderate  { border-left-color: #92400e; }
.result-prob.moderate  { color: #92400e; }
.result-label.moderate { color: #92400e; }

/* Patient summary card ----------------------------------------------- */
.summary-card {
    border: 1px solid #d9d3c6;
    background: #ffffff;
    border-radius: 3px;
    padding: .3rem 1.1rem;
}
.summary-row {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    padding: .55rem 0;
    border-bottom: 1px solid #eee8db;
    font-size: .92rem;
}
.summary-row:last-child { border-bottom: none; }
.summary-row .k { color: #7a8794; }
.summary-row .v { color: #22303c; font-weight: 600; text-align: right; }

/* Stale-result banner -------------------------------------------------- */
.stale-banner {
    border: 1px solid #e0c891;
    background: #fbf3de;
    color: #7a5c17;
    border-radius: 3px;
    padding: .55rem .9rem;
    font-size: .85rem;
    margin-bottom: .8rem;
}

/* Clinical flag card --------------------------------------------------- */
.flag-card {
    border: 1px solid #d9d3c6;
    background: #ffffff;
    border-radius: 3px;
}
.flag-row {
    display: flex;
    align-items: flex-start;
    gap: .55rem;
    padding: .5rem .75rem;
    border-bottom: 1px solid #eee8db;
}
.flag-row:last-child { border-bottom: none; }
.flag-dot {
    width: .5rem; height: .5rem; border-radius: 50%;
    margin-top: .3rem; flex: 0 0 auto;
}
.flag-row.high .flag-dot     { background: #9b2c2c; }
.flag-row.moderate .flag-dot { background: #92400e; }
.flag-row.low .flag-dot      { background: #2f6b46; }
.flag-title  { display: block; font-size: .82rem; font-weight: 600; color: #22303c !important; }
.flag-detail { display: block; font-size: .76rem; color: #7a8794 !important; }

/* Compact alert banners (contradiction / lifestyle risk) --------------- */
.alert-banner {
    border-radius: 3px;
    padding: .5rem .75rem;
    font-size: .8rem;
    margin-top: .6rem;
    border: 1px solid;
}
.alert-banner.error   { background: #f7e7e3; border-color: #e3b3a5; color: #7a3223 !important; }
.alert-banner.warning { background: #fbf3de; border-color: #e0c891; color: #7a5c17 !important; }

/* Sidebar ----------------------------------------------------------- */
section[data-testid="stSidebar"] { background:#f2efe8; border-right:1px solid #ddd6c8; }
section[data-testid="stSidebar"] h2 { font-family:'Lora',serif !important; color:#1f2b38 !important; }
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span { color:#22303c !important; }
/* The rule above (higher specificity than the general button-text fix below)
   would otherwise force dark navy text onto the "Run risk assessment"
   primary button, which lives in the sidebar and has a dark navy background
   of its own — text and background would be indistinguishable. */
section[data-testid="stSidebar"] [data-testid="stBaseButton-primary"] p { color: #ffffff !important; }
section[data-testid="stSidebar"] [data-testid="stLogoSpacer"] { display: none; }
section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] { gap: .6rem; }
section[data-testid="stSidebar"] hr { margin: .5rem 0; }
section[data-testid="stSidebar"] h2 { margin-bottom: .15rem; }
.field-group-label {
    font-family: 'Source Sans 3', sans-serif;
    text-transform: uppercase;
    letter-spacing: .12em;
    font-size: .68rem;
    font-weight: 600;
    color: #8a8577 !important;
    margin: .9rem 0 .2rem 0;
}

footer, #MainMenu { visibility: hidden; }
.app-footer {
    margin-top: 2.5rem; padding-top: 1rem;
    border-top: 1px solid #e3ddd0;
    font-size: .8rem; color: #9a9384; text-align:center;
    font-family: 'Source Sans 3', sans-serif;
}

/* st.caption() ------------------------------------------------------- */
/* Streamlit dims captions via `opacity: 0.6` on the container rather than
   an explicit color, which — composited over our cream background instead
   of Streamlit's default white — reads as too faint. Force full opacity
   and set the muted tone explicitly so it's deliberate and consistent. */
[data-testid="stCaptionContainer"] { opacity: 1 !important; }
[data-testid="stCaptionContainer"] p { color: #5c6672 !important; }

/* Expander headers + general body text --------------------------------- */
/* Belt-and-suspenders: pin these explicitly rather than relying on
   Streamlit's own (theme-dependent) defaults, since native components have
   twice now picked up dark-mode colors despite the app being locked to a
   light theme via .streamlit/config.toml. */
[data-testid="stExpander"] summary { color: #22303c !important; opacity: 1 !important; }
[data-testid="stExpander"] summary svg { fill: #22303c !important; opacity: 1 !important; }
/* The expander's own background is transparent by default, so it merely
   inherits whatever's behind it — normally our cream .stApp background, but
   that's an assumption, not a guarantee. Force it explicitly so text inside
   (e.g. .sec-label headings) always sits on a real light background. */
[data-testid="stExpander"] { background-color: #fbfaf7; }
[data-testid="stExpanderDetails"] { background-color: #fbfaf7; }
[data-testid="stMarkdownContainer"] p { color: #22303c; }

/* st.metric (AUC-ROC / Recall / Precision / F1 Score) — the value/label/delta
   text has no color of its own in our CSS at all, so like every other native
   widget above it renders with whatever Streamlit's actual active theme
   dictates, which can be a light color meant for a dark backdrop. */
[data-testid="stMetricValue"] { color: #22303c !important; }
[data-testid="stMetricLabel"] { color: #7a8794 !important; }
[data-testid="stMetricDelta"] { color: #22303c !important; }

/* Primary button ("Run risk assessment") sits on a dark navy background
   (primaryColor) — the blanket rule above would otherwise force the same
   dark navy onto its label, making it unreadable. White is the correct
   contrast choice against a dark background. */
[data-testid="stBaseButton-primary"] p { color: #ffffff !important; }

/* Secondary buttons (LIME, PDF/CSV downloads) have no primaryColor fill, so
   their surface is entirely native-theme-driven — if the active Streamlit
   theme ever drifts from our custom config, they can render with a dark
   fill while the rule above still forces dark text onto their label,
   making them unreadable. Give them a fully self-contained appearance
   instead of relying on inherited theme colors. */
[data-testid="stBaseButton-secondary"] {
    background-color: #ffffff !important;
    border-color: #2c3e50 !important;
}
[data-testid="stBaseButton-secondary"] p { color: #2c3e50 !important; }
</style>
"""


def inject_css() -> None:
    st.markdown(APP_CSS, unsafe_allow_html=True)
