# Required for `setuptools` to find modules in this package
from pathlib import Path

COMPLETION_DIR = Path(__file__).parent
COMPLETION_SCRIPT_PATH = COMPLETION_DIR / "firewheel_completion.sh"
