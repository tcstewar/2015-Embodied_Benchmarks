import os
import sys

import numpy as np
import pylab

path = sys.argv[1]

data_x = []
data_y = []
for fn in os.listdir(path):
    if fn.endswith('.txt'):
        with open(os.path.join(path, fn)) as f:
            text = f.read()
        d = dict()
        exec(text, d)

        x = d['_delay']
        y = d['rmse']

        data_x.append(x)
        data_y.append(y)

#data_x = data_x[:30]
#data_y = data_y[:30]

do_gp = True

pylab.figure(figsize=(8,4))

if do_gp:
    import pylab
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
    pylab.scatter(data_x, data_y, marker='x', color='k')


pylab.xlim(0, 0.04)
pylab.xlabel('delay (s)')
pylab.ylabel('rmse')
pylab.savefig('plot_vary.png', dpi=100)
