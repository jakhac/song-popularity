import os
from pathlib import Path
from typing import Any, Callable, Dict, List, Tuple

import matplotlib as mpl
import matplotlib.pyplot as plt
from dotenv import load_dotenv

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


def plots_from_list(
    metrics: str,
    plots: List[Tuple[Callable, Dict[str, Any], str, str, str]],
    model_type: str,
    file_name: str,
):
    """Create a figure from a list of plots and stores it as pdf.

    Args:
        metrics (str): information to be printed on top of the pdf
        plots (List[Tuple[Callable, Dict[str, Any], str, str, str]]): list of tuples: (plot function, plot function arguments, xlabel, ylabel, title)
        model_type (str): music, artist or lyrics; parent folder of pdf
        file_name (str): name of the pdf file

    Raises:
        ValueError: pdf with `file_name` already exists
    """
    # get or create target directoy
    model_dir = Path(DATA_PATH) / "models" / model_type
    if not model_dir.is_dir():
        model_dir.mkdir(parents=True, exist_ok=True)

    # specify target file
    target_file = model_dir / (file_name + ".pdf")
    if target_file.is_file():
        raise ValueError(f"PDF with name {file_name} already exists.")

    # create plot
    fig = plt.figure(figsize=(12, 3 + (len(plots) * 3)))
    fig.suptitle(file_name, fontsize=15)

    # add text
    fig.add_subplot(1, 1, 1)
    plt.gca().invert_yaxis()
    plt.figtext(x=0.05, y=0.8, s=(metrics), wrap=True)
    plt.axis("off")

    # map list on subplots
    for idx, plot_data in enumerate(plots, start=3):
        ax = fig.add_subplot(int(len(plot_data) / 2) + 1, 2, idx)
        ax.set_xlabel(plot_data[2])
        ax.set_ylabel(plot_data[3])
        ax.set_title(plot_data[4])

        # call plot function at [0] with arguments in dict at [1]
        plot_data[0](**plot_data[1])

    # spacing between plots
    fig.tight_layout()

    # Different backend that does not show plots to user
    mpl.use("Agg")
    fig.savefig(target_file)
