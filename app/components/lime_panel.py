from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

from model import model, features

try:
    from lime.lime_tabular import LimeTabularExplainer
    LIME_AVAILABLE = True
except ImportError:
    LIME_AVAILABLE = False


def render_lime_panel(result: dict | None) -> None:
    """LIME — Independent Explanation Validation expander. No-op until a
    prediction has been run.
    """
    if result is None:
        return

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
                            f'SHAP and LIME agree on **{len(overlap)}/3** '
                            f'top risk drivers  ({", ".join(sorted(overlap))}).\n\n'
                            'Cross-method agreement strengthens confidence in '
                            'the explanation.'
                        )
                    else:
                        st.warning(
                            'SHAP and LIME highlight different top features. '
                            'Review both explanations independently before '
                            'drawing clinical conclusions.'
                        )
