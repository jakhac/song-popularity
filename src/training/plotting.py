import math
import os
from pathlib import Path
from typing import Any, Callable, Dict, List, Tuple

import matplotlib as mpl
import matplotlib.pyplot as plt
from dotenv import load_dotenv
from matplotlib import axes
from sklearn.metrics._plot.confusion_matrix import plot_confusion_matrix

from .postprocessing import get_metrics

load_dotenv()

DATA_PATH = os.getenv("DATA_PATH")


def disp_scatter(
    x: any,
    y: any,
    x_label: str = None,
    y_label: str = None,
    plot_name: str = None,
):
    """Displays a scatter plot.

    Args:
        x (any): list of data for x-axis
        y (any): list of data for y-axis data
        x_label (str, optional): label for x-axis. Defaults to None.
        y_label (str, optional): label for y-axis. Defaults to None.
        plot_name (str, optional): title of plot. Defaults to None.
    """
    plt.title(plot_name)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.scatter(x, y, s=5, alpha=0.5)
    plt.show()


def plots_from_list(
    title: str,
    plots: List[Tuple[Callable, Dict[str, Any], str, str, str]],
    model_type: str = None,
    text: str = None,
    save: bool = False,
    cols: int = 2,
):
    """Create a figure from a list of plots. Stored as pdf if save is True.

    Args:
        title (str): title on the document + file name

        plots (List[Tuple[Callable, Dict[str, Any], str, str, str]]): list of tuples:
            (plot function, plot function arguments, title, xlabel, ylabel)

        text (str): information to be printed on top of the document. Defaults to None.

        model_type (str, optional): name of parent folder for pdf. Defaults to None.

        save (bool, optional): true to save file. Defaults to False.

        cols (int, optional): number of columns of generated figure. Defaults to 2.

    Raises:
        ValueError: File with `file_name` already exists
    """

    if save:
        # get or create target directoy
        model_dir = Path(DATA_PATH) / "models" / model_type
        if not model_dir.is_dir():
            model_dir.mkdir(parents=True, exist_ok=True)

        # specify target file
        target_file = model_dir / (title + ".jpg")
        if target_file.is_file():
            raise ValueError(f"File with name {title} already exists.")

    # create plot
    fig = plt.figure(figsize=(cols * 6, (len(plots) * 3)))
    fig.suptitle(title, fontsize=15)

    #  add text
    if text:
        ax = fig.add_subplot(cols, 1, 1)
        ax.text(x=0.05, y=0.9, s=(text), wrap=True)
        plt.axis("off")

    # map list on subplots
    for idx, plot_data in enumerate(plots, start=(cols + 1)):
        ax = fig.add_subplot(cols + int(math.ceil((len(plots) / cols))), cols, idx)
        ax.set_title(plot_data[2])
        ax.set_xlabel(plot_data[3])
        ax.set_ylabel(plot_data[4])

        # for confusion matrix, add axis to arguments
        fun = plot_data[0]

        if fun != "text" and fun.__name__ == "plot_confusion_matrix":
            plot_data[1]["ax"] = ax

        if fun == "text":
            # call text function of axis with arguments in dict at [1]
            ax.text(**plot_data[1])
            plt.axis("off")
        else:
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
    """Generates a list confusion matrices for the classifiers in `clf_list`.

    Args:
        X_test (List[any]): test data samples
        y_test (List[any]): test data classes
        clf_list (List[any]): list of classifiers
        clf_annotations (List[str], optional): TODO. Defaults to None.

    Returns:
        List[Tuple[Callable, Dict[str, Any]]: list of plots
    """

    # metrics
    metrics_list = list(map(lambda clf: (get_metrics(clf, X_test, y_test)), clf_list))

    text_plots = list(
        map(
            lambda txt: (
                "text",
                {"x": 0.05, "y": 0.4, "s": txt, "wrap": True},
                None,
                None,
                None,
            ),
            metrics_list,
        )
    )

    # confusion matrices
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
                None,
                None,
                str(clf),
            ),
            clf_list,
        )
    )

    # normalized confusion matrices
    cf_matrices_norm = list(
        map(
            lambda clf: (
                plot_confusion_matrix,
                {
                    "estimator": clf,
                    "X": X_test,
                    "y_true": y_test,
                    "cmap": plt.cm.Blues,
                    "normalize": "true",
                    "values_format": ".2f",
                },
                None,
                None,
                str(clf),
            ),
            clf_list,
        )
    )

    # zip for final list to be ordered: text, cf_matrix, cf_matrix_norm
    zipped_plots = zip(text_plots, cf_matrices, cf_matrices_norm)
    return [plot for tpl in zipped_plots for plot in tpl]
