import numpy as np

import matplotlib.pyplot as plt


def scatter_2D(ax, x, y, color, clf=None, x_label="X", y_label="Y", title="2D Scatter"):
    """

    :param x:
    :param y:
    :param color:
    :param clf: If given, a mesh will be plotted showing the decision boundaries.
    :return:
    """
    if clf is not None:
        x_range = x.max() - x.min()
        y_range = y.max() - y.min()
        x_padding = x_range * 0.1
        y_padding = y_range * 0.1
        x_min, x_max = x.min() - x_padding, x.max() + x_padding
        y_min, y_max = y.min() - y_padding, y.max() + y_padding
        # We want a 100x100 grid
        xx, yy = np.meshgrid(np.arange(x_min, x_max, x_range / 100),
                             np.arange(y_min, y_max, y_range / 100))

        Z = clf.predict(np.c_[xx.ravel(), yy.ravel()])
        Z = Z.reshape(xx.shape)
        Z_proba = clf.predict_proba(np.c_[xx.ravel(), yy.ravel()])[:, 1]
        Z_proba = Z_proba.reshape(xx.shape)

        ax.contourf(xx, yy, Z_proba, cmap=plt.get_cmap("RdYlGn"), alpha=0.5)
        ax.set_xlim(xx.min(), xx.max())
        ax.set_ylim(yy.min(), yy.max())

    ax.scatter(x, y, c=color, cmap=plt.get_cmap("RdYlGn"))

    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    # ax.set_xticks(())
    # ax.set_yticks(())
    ax.set_title(title)


def scatter_3D(ax, x, y, z, color, clf=None, x_label="X", y_label="Y", z_label="Z", title="3D Scatter"):
    ax.scatter(x, y, z, c=color)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.set_zlabel(z_label)
    ax.set_title(title)
    plt.show()
