from datetime import datetime

import pandas as pd
import streamlit as st


def render_trust_dashboard() -> None:
    """Model Trust Dashboard expander: deployed-model metrics, comparative
    performance across candidate models, dataset/XAI/validation info, and
    the session audit log with CSV export. Works even with no prediction run.
    """
    with st.expander('Model Trust Dashboard', expanded=False):

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

        st.divider()
        st.markdown(
            '<div class="sec-label">Session Audit Log</div>',
            unsafe_allow_html=True
        )

        if st.session_state.get('history'):
            audit_df = pd.DataFrame(st.session_state['history'])
            st.dataframe(audit_df, use_container_width=True, hide_index=True)
            st.download_button(
                label='Download audit log (CSV)',
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
