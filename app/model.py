import joblib
import shap

from constants import MODELS_DIR

# Load saved model files from Colab
model     = joblib.load(MODELS_DIR / 'cardio_model.pkl')
scaler    = joblib.load(MODELS_DIR / 'cardio_scaler.pkl')
features  = joblib.load(MODELS_DIR / 'feature_names.pkl')
# Built locally instead of unpickling shap_explainer.pkl: SHAP's TreeExplainer
# embeds numba-JIT code objects whose pickle format isn't compatible across
# Python versions (the file was saved from a different Python than this machine runs).
explainer = shap.TreeExplainer(model)
