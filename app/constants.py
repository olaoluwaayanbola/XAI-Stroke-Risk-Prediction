from dataclasses import dataclass
from pathlib import Path

# Resolve paths relative to this file so they work regardless of the launch directory
APP_DIR = Path(__file__).parent
ASSETS_DIR = APP_DIR / 'assets'
MODELS_DIR = APP_DIR.parent / 'models'

# Shared label maps — single source of truth for both the input widgets and the
# read-back summary card, so the two can never drift out of sync.
GENDER_LABELS = {1: 'Female', 2: 'Male'}
LAB_LEVELS    = {1: 'Normal', 2: 'Above Normal', 3: 'Well Above'}
YES_NO        = {0: 'No', 1: 'Yes'}
ACTIVITY      = {1: 'Active', 0: 'Not active'}


def risk_tier(p: float) -> str:
    """Return 'High', 'Moderate', or 'Low' for a given probability."""
    if p >= 0.70:
        return 'High'
    if p >= 0.40:
        return 'Moderate'
    return 'Low'


@dataclass(frozen=True)
class PatientInputs:
    """Snapshot of every sidebar input. Compares by value, so it doubles as the
    staleness check: `session_state['result_inputs'] != current_inputs`."""
    age: int
    gender: int
    sys_bp: int
    dia_bp: int
    chol: int
    gluc: int
    bmi: float
    smoking: int
    alcohol: int
    active: int
