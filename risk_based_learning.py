import numpy as np
from matplotlib import pyplot as plt
from scipy.optimize import minimize
from dcr import *

# d = np.array([0, 0, 0, 1])
# log_like = np.zeros(100)
# pi = np.zeros(100)
# for pi_s in range(0, 100, 1):
#     loglike_indiv = d * np.log((pi_s+1)/100) + (1-d) * np.log(1-(pi_s+1)/100)
#     pi[pi_s] = pi_s
#
#     log_like[pi_s] = np.sum(loglike_indiv)
# plt.scatter(pi/100, log_like, marker='o')
# plt.show()


def func_loglike3(x, d, beta):
    pd_pred = np.exp(beta*x)/(1+np.exp(beta*x))
    loglike_indiv = d * np.log(pd_pred) + (1-d) * np.log(1-pd_pred)
    loglike = np.sum(loglike_indiv)
    return loglike


beta = np.linspace(-0.01, 0.009)
loglike_beta = np.zeros(beta.shape)
x = np.array([400, 300, 200, 100])
d = np.array([0, 0, 1, 1])

for i, beta_s in enumerate(beta):
    loglike_beta[i] = func_loglike3(x, d, beta_s)


def func_loglike4(beta):
    pd_pred = np.exp(beta*x)/(1+np.exp(beta*x))
    loglike_indiv = d * np.log(pd_pred) + (1-d) * np.log(1-pd_pred)
    neg_loglike = -np.sum(loglike_indiv)
    return neg_loglike

minimize(func_loglike4,0, method='Nelder-Mead', options={'disp': True})

model_logit = sm.Logit(d, x)
results = model_logit.fit()

