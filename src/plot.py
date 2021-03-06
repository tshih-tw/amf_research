"""
Utility functions for plotting
"""
import argparse
import os.path
import sys

import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.patches as patches
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

from convertible_bond import A, P, C, T, S as Conv
from model import FDEModel, CrankNicolsonScheme

__all__ = ["payoff", "plot_model", "plotmain"]

colourise = cm.gist_ncar
PUT   = 0. / 6
CALL  = 1. / 6
CONV  = 2. / 6
FCONV = 3. / 6
REDEM = 4. / 6
HOLD  = 5. / 6


def payoff(t, S, V, I):
    if t in A and t != T:
        V -= A.C

    if V == S and t in Conv:
        if t in C and t != T and I > S:
            return FCONV
        else:
            return CONV
    elif t == T:
        return REDEM
    elif t in P and V == P.payoff.strike(t):
        return PUT
    elif t in C and V == C.payoff.strike(t):
        return CALL
    else:
        return HOLD


def choices(P):
    colours = np.zeros((len(P.S), len(P.t)))
    for y, t in zip(range(len(P.t)), P.t):
        for x, S in zip(range(len(P.S)), P.S):
            #print (y, t), (x, S)
            colours[x, y] = payoff(t, S, P.V[y][x], P.I[y][x])
    return colourise(colours)


def legend(ax):
    proxy = []
    descr = []
    def colour(col):
        return patches.Rectangle((0, 0), 1, 1, fc=colourise(col))

    proxy.append(colour(PUT))
    descr.append("Put")

    proxy.append(colour(CALL))
    descr.append("Call")

    proxy.append(colour(CONV))
    descr.append("Conversion")

    proxy.append(colour(FCONV))
    descr.append("Forced conversion")

    proxy.append(colour(REDEM))
    descr.append("Redemption")

    proxy.append(colour(HOLD))
    descr.append("Hold")
    ax.legend(proxy, descr, loc=2, prop={'size': 10})


def plot_strips(ax, X, Y, Z, padding=0, facecolors=None):
    """Plot the graph as a series of strips along the Y axis."""
    Yn = (Y[:-1] + Y[1:]) / 2.
    Yn = np.append(Y[0] - (Y[1] - Y[0]) / 2., Yn)
    Yn = np.append(Yn, Y[-1] + (Y[-1] - Y[-2]) / 2.)
    for x in range(len(X)):
        if x == 0:
            offset = (X[1] - X[0]) / 2.
        elif x == len(X) - 1:
            offset = (X[-1] - X[-2]) / 2.
        else:
            offset = (X[x + 1] - X[x - 1]) / 4.
        offset -= padding / 2.
        Xs, Ys = np.meshgrid([X[x] - offset, X[x] + offset], Yn)
        Zs = (Z[:-1, x] + Z[1:, x]) / 2.
        Zs = np.append(Z[0, x] - (Z[1, x] - Z[0, x]) / 2., Zs)
        Zs = np.append(Zs, Z[-1, x] + (Z[-1, x] - Z[-2, x]) / 2.)
        Zs = np.array([Zs, Zs]).T
        colours = np.zeros(Xs.shape + (4,))
        colours[0:-1, 0] = facecolors[:, x]
        ax.plot_surface(Xs, Ys, Zs, linewidth=0, cstride=1, rstride=1,
                        facecolors=colours, alpha=0.75)


def plot_model(ax, dS, payoff):
    N = 40
    model = FDEModel(N, dS, payoff)
    P = model.price(0, 250, 125, scheme=CrankNicolsonScheme)
    colours = choices(P)
    plot_strips(ax, P.t, P.S[:100], np.array(P.V)[:, :100].T, facecolors=colours[:100])
    ax.set_xlabel("Time")
    ax.set_ylabel("Stock Price")
    ax.set_zlabel("Portfolio Value")
    legend(ax)

def plotmain(main):
    name = os.path.basename(sys.argv[0])[:-3]

    parser = argparse.ArgumentParser()
    parser.add_argument('--format', '-f', type=str, default='pdf',
                        help='Image format')
    parser.add_argument('--show', '-s', default=False, action='store_true',
                        help='Show image')
    parser.add_argument('--backend', '-b', type=str, help='Rendering backend')
    args = parser.parse_args()

    if args.backend:
        plt.switch_backend(args.backend)
    elif args.show:
        plt.switch_backend('Qt4Agg')
    else:
        plt.switch_backend('cairo')

    main()

    if args.show:
        plt.show()
    else:
        plt.savefig("../common/%s.%s" % (name, args.format))
