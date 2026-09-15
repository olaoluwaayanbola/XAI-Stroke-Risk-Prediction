from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

from model import model, features, scaler

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
                     expanded=st.session_state.get('lime_expanded', False)):

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

                    # Synthetic training reference from real feature
                    # statistics (original training data is not shipped
                    # with the app, but its fitted mean/std are, via the
                    # scaler). Continuous features are sampled from a
                    # Gaussian centred on the real population stats;
                    # categorical/binary features are sampled as discrete
                    # levels so LIME perturbs them realistically.
                    rng = np.random.default_rng(42)
                    continuous = {0: (18, 90), 2: (60, 250),
                                  3: (40, 200), 9: (10, 60)}
                    categorical_idx = [1, 4, 5, 6, 7, 8]
                    # Category prevalence from the source cardiovascular
                    # dataset (not uniform — e.g. most patients are
                    # non-smokers with normal labs). Sampling uniformly
                    # here would make LIME's perturbation neighbourhood
                    # over-represent rare/abnormal categories, exaggerating
                    # local nonlinearity and deflating the fidelity score.
                    categorical = {
                        1: ([1, 2],       [0.65, 0.35]),        # gender
                        4: ([1, 2, 3],    [0.75, 0.135, 0.115]), # cholesterol
                        5: ([1, 2, 3],    [0.85, 0.075, 0.075]), # glucose
                        6: ([0, 1],       [0.91, 0.09]),         # smoking
                        7: ([0, 1],       [0.95, 0.05]),         # alcohol
                        8: ([0, 1],       [0.20, 0.80]),         # active
                    }

                    training_ref = np.zeros((1000, len(features)))
                    for idx, (lo, hi) in continuous.items():
                        training_ref[:, idx] = np.clip(
                            rng.normal(scaler.mean_[idx],
                                       scaler.scale_[idx], 1000),
                            lo, hi
                        )
                    for idx, (values, probs) in categorical.items():
                        training_ref[:, idx] = rng.choice(
                            values, size=1000, p=probs
                        )

                    lime_explainer = LimeTabularExplainer(
                        training_data=training_ref,
                        feature_names=features,
                        class_names=['No CVD', 'Has CVD'],
                        categorical_features=categorical_idx,
                        mode='classification',
                        random_state=42
                    )

                    lime_result = lime_explainer.explain_instance(
                        data_row=result['data'],
                        predict_fn=model.predict_proba,
                        num_features=10
                    )
                    st.session_state['lime_result']   = lime_result
                    st.session_state['lime_expanded'] = True

                st.rerun()

            if 'lime_result' in st.session_state:

                lime_r = st.session_state['lime_result']

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
