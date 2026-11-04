import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
DATA = ROOT / "data"


def prepare():
    REPORTS.mkdir(exist_ok=True)
    DATA.mkdir(exist_ok=True)
    plt.rcParams.update(
        {
            "figure.facecolor": "#f7f9fc",
            "axes.facecolor": "#f7f9fc",
            "axes.spines.top": False,
            "axes.spines.right": False,
            "font.size": 11,
            "axes.titleweight": "bold",
        }
    )


def save_metrics(metrics):
    (REPORTS / "metrics.json").write_text(json.dumps(metrics, indent=2, ensure_ascii=False) + "\n")
