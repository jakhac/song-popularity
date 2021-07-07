import matplotlib.pyplot as plt


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
