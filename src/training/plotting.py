import matplotlib.pyplot as plt
import matplotlib as mpl
from typing import List
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

DATA_PATH = os.getenv("DATA_PATH")


def disp_scatter(
    x: any,
    y: any,
    x_label: str = None,
    y_label: str = None,
    plot_name: str = None,
):
    plt.title(plot_name)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.scatter(x, y, s=5, alpha=0.5)
    plt.show()


# (x, y, x_label, y_label, plt_name)
def create_plots(metrics: str, data: List[float], model_type: str):
    fig = plt.figure(figsize=(12, 3 + (len(data) * 3)))

    fig.suptitle(metrics + "\n\n", fontsize=15)

    for i, d in enumerate(data, start=1):
        ax = fig.add_subplot(int(len(data) / 2) + 1, 2, i)
        ax.set_xlabel(d[2])
        ax.set_ylabel(d[3])
        ax.set_title(d[4])
        ax.scatter(d[0], d[1], s=5, alpha=0.5)

    fig.tight_layout()

    model_dir = Path(DATA_PATH) / "models" / model_type
    if not model_dir.is_dir():
        model_dir.mkdir(parents=True, exist_ok=True)

    # Different backend that does not show plots to user
    mpl.use("Agg")
    fig.savefig(model_dir / "plot1.pdf")
