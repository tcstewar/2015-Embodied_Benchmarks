import os
import sys

import numpy as np
import pylab

pylab.figure(figsize=(12,8))

do_logx = True

index = 1
for D in [1, 5, 10, 15]:
    path = 'vary_neuronsD%d_spinn' % D

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

    pylab.subplot(2, 2, index)

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
    if index in [3, 4]:
        pylab.xlabel('number of neurons')
    if index in [1,3]:
        pylab.ylabel('rmse')
    pylab.ylim(-0.05, 0.5)
    index += 1
pylab.savefig('fig_vary_neurons_spinn.png', dpi=100)
