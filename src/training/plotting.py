import math
import os
from pathlib import Path
from typing import Any, Callable, Dict, List, Tuple

import matplotlib as mpl
import matplotlib.pyplot as plt
from dotenv import load_dotenv
from sklearn.metrics._plot.confusion_matrix import plot_confusion_matrix

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
    text: str,
    plots: List[Tuple[Callable, Dict[str, Any], str, str, str]],
    title: str,
    model_type: str = None,
    save: bool = False,
    cols: int = 2,
):
    """Create a figure from a list of plots. Stored as pdf if save is True.

    Args:
        text (str): information to be printed on top of the pdf
        plots (List[Tuple[Callable, Dict[str, Any], str, str, str]]): list of tuples: (plot function, plot function arguments, xlabel, ylabel, title)
        title (str): name of the pdf file
        model_type (str, optional): name of parent folder for pdf. Defaults to None.
        save (bool, optional): true to save file. Defaults to False.
        cols (int, optional): number of columns of generated figure. Defaults to 2.

    Raises:
        ValueError: pdf with `file_name` already exists
    """

    if save:
        # get or create target directoy
        model_dir = Path(DATA_PATH) / "models" / model_type
        if not model_dir.is_dir():
            model_dir.mkdir(parents=True, exist_ok=True)

        # specify target file
        target_file = model_dir / (title + ".jpg")
        if target_file.is_file():
            raise ValueError(f"PDF with name {title} already exists.")

    # create plot
    fig = plt.figure(figsize=(12, (len(plots) * 3)))
    fig.suptitle(title, fontsize=15)

    # add text
    ax = fig.add_subplot(2, 1, 1)
    ax.text(x=0.05, y=0.9, s=(text), wrap=True)
    plt.axis("off")

    # map list on subplots
    for idx, plot_data in enumerate(plots, start=3):
        # print(2 + int(math.ceil((len(plots) / 2))), cols, idx)
        ax = fig.add_subplot(2 + int(math.ceil((len(plots) / 2))), cols, idx)
        ax.set_xlabel(plot_data[2])
        ax.set_ylabel(plot_data[3])
        ax.set_title(plot_data[4])

        # for confusion matrix, add axis to arguments
        fun = plot_data[0]
        # print(fun)

        if fun.__name__ == "plot_confusion_matrix":
            plot_data[1]["ax"] = ax

        # call plot function at [0] with arguments in dict at [1]
        plot_data[0](**plot_data[1])

    # spacing between plots
    fig.tight_layout()

    if save:
        # Different backend that does not show plots to user
        mpl.use("Agg")
        fig.savefig(target_file)
    else:
        plt.show()


def generate_model_plots(
    X_test: List[any],
    y_test: List[any],
    clf_list: List[any],
    clf_annotations: List[str] = None,
):
    plt_list = []

    # get predictions
    y_predictions = list(map(lambda clf: clf.predict(X_test), clf_list))

    # add confusion matrices
    cf_matrices = list(
        map(
            lambda clf: (
                plot_confusion_matrix,
                {
                    "estimator": clf,
                    "X": X_test,
                    "y_true": y_test,
                    "cmap": plt.cm.Blues,
                    "normalize": None,
                    "values_format": ".2f",
                },
                "Title",
                None,
                None,
            ),
            clf_list,
        )
    )
    plt_list += cf_matrices

    return plt_list
