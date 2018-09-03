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
        x_min, x_max = x.min() - 1, x.max() + 1
        y_min, y_max = y.min() - 1, y.max() + 1
        # We want a 100x100 grid
        x_stepsize, y_stepsize = (x_max - x_min) / 100, (y_max - y_min) / 100
        xx, yy = np.meshgrid(np.arange(x_min, x_max, x_stepsize),
                             np.arange(y_min, y_max, y_stepsize))

        Z = clf.predict(np.c_[xx.ravel(), yy.ravel()])
        Z = Z.reshape(xx.shape)
        ax.contourf(xx, yy, Z, alpha=0.5)
        ax.set_xlim(xx.min(), xx.max())
        ax.set_ylim(yy.min(), yy.max())

    ax.scatter(x, y, c=color, s=20, edgecolors='k')

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
