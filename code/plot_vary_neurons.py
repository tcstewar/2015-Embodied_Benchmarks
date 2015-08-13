import os
import sys

import numpy as np
import pylab

import bootstrapci

do_logx = True

D = int(sys.argv[1])
path = 'vary_neuronsD%d' % D

data_x = []
data_y = []
for fn in os.listdir(path):
    if fn.endswith('.txt'):
        with open(os.path.join(path, fn)) as f:
            text = f.read()
        d = dict()
        try:
            exec(text, d)
        except:
            continue

        x = d['_n_neurons']
        y = d['rmse']

        if do_logx:
            x = np.log2(x)
        if y > 1.0:
            continue

        data_x.append(x)
        data_y.append(y)
        print x, y

#data_x = data_x[:30]
#data_y = data_y[:30]

data_x = np.array(data_x)
data_y = np.array(data_y)

do_gp = False

pylab.figure(figsize=(8,5))

if do_gp:
    import GPy

    X = np.array(data_x)
    X.shape = X.shape[0], 1
    Y = np.array(data_y)
    Y.shape = Y.shape[0], 1


    kernel = GPy.kern.RBF(input_dim=1, variance=1, lengthscale=0.005)
    #kernel = kernel+GPy.kern.RBF(input_dim=1, variance=1, lengthscale=0.005)
    #kernel = GPy.kern.Linear(1)
    #kernel = GPy.kern.Brownian(1)
    m = GPy.models.GPRegression(X, Y,kernel)
    #m = GPy.models.SparseGPRegression(X, Y,kernel)
    #m = GPy.models.GPCoregionalizedRegression([X], [Y],kernel)
    #m = GPy.models.GPHeteroscedasticRegression(X, Y,kernel)
    #m = GPy.models.GPVariationalGaussianApproximation(X, Y, kernel)
    #m = GPy.models.SparseGPRegression(X,Y,Z=np.random.rand(10,1)*0.04, kernel=kernel)
    m.optimize('bfgs', messages=True)
    #m.optimize('tnc', messages=True)

    #print help(m.optimize)


    #m.optimize('bfgs', max_iters=100)
    #m.optimize_restarts(num_restarts=10)
    m.optimize()

    print m

    m.plot()

else:


    def weighted_avg_and_std(values, weights):
        average = np.average(values, weights=weights)
        variance = np.average((values-average)**2, weights=weights)
        return (average, np.sqrt(variance))

    low = []
    high = []
    var = 1.0
    x = np.linspace(0,10, 100)
    for xx in x:
        w = np.exp(-((data_x-xx)**2)/(2*var**2))
        try:
            mean, sd = weighted_avg_and_std(data_y, w)
        except ZeroDivisionError:
            mean, sd = 0.0, 0.0
        ci = mean - 1*sd, mean+1*sd
        low.append(ci[0])
        high.append(ci[1])

    pylab.fill_between(x, low, high, color='#aaaaaa')

    pylab.scatter(data_x, data_y, s=30, marker='x', color='k')


if D > 1:
    pylab.title('Adaptive control of %d interacting values' % D)
else:
    pylab.title('Adaptive control of 1 value')

pylab.xlim(-1, 10)
xticks = [0, 2, 4, 6, 8, 10]
pylab.xticks(xticks, ['%d' % (2**xx) for xx in xticks])
pylab.xlabel('number of neurons')
pylab.ylabel('rmse')
pylab.ylim(-0.05, 0.5)
pylab.savefig(path + '.png', dpi=100)
