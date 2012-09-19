"""
Comparative graph between AFV03 figure 4 and this model.
"""
import copy
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy
numpy.seterr(divide="ignore")

from convertible_bond import dS, dS_total, payoff, B
from model import FDEModel

def main():
    N = 200
    S = range(80, 121)
    Sl = 0
    Su = 200
    model1 = FDEModel(N, dS_total, payoff)
    model2 = FDEModel(N, dS, payoff)
    B.R = 1.0
    plt.plot(S, model1.price(Sl, Su, N).V[0][S])
    plt.plot(S, model2.price(Sl, Su, N).V[0][S])
    B.R = 0.5
    plt.plot(S, model1.price(Sl, Su, N).V[0][S])
    B.R = 0.0
    plt.plot(S, model1.price(Sl, Su, N).V[0][S])
    plt.ylim([100, 150])
    plt.xlabel("Stock Price")
    plt.ylabel("Convertible Bond Price")
    plt.legend(["Total default (R=100%)", "No default", "Total default (R=50%)", "Total default (R=0%)"], loc=2)
    plt.savefig("../common/fig_afv03_4.png")
    plt.savefig("../common/fig_afv03_4.svg")
    #plt.show()

if __name__ == "__main__":
    main()