import os
import sys
import bootstrapci

import numpy as np
import pylab

fig = pylab.figure(figsize=(10,5))
ax = fig.add_subplot(1,1,1)

do_logx = False

error_bars = []
error_means = []
all_data = []
index = 1
#for n_neurons in [0, 5200, 1500, 500]:
for n_neurons in [5200, 1500, 500]:
    path = 'vary_neurons3_%d' % n_neurons

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

            if d['_seed'] == 20:
                continue

            x = d['_D']
            y = d['rmse']

            if do_logx:
                x = np.log2(x)
            if y > 1.0:
                continue
                y = 1.0

            data_x.append(x)
            data_y.append(y)
            print x, y

    #data_x = data_x[:30]
    #data_y = data_y[:30]

    data_x = np.array(data_x)
    data_y = np.array(data_y)
    all_data.append(data_y)

    mean = np.mean(data_y)
    sd = np.std(data_y)
    ci = bootstrapci.bootstrapci(data_y, np.mean)

    width = 0.3

    pylab.fill_between([index-width, index+width], mean-sd, mean+sd, color='#aaaaaa')
    pylab.scatter(np.random.uniform(index-width, index+width, data_y.shape), data_y, s=30, marker='x', color='k')
    error_means.append(mean)
    error_bars.append([mean-ci[0], ci[1]-mean])
    index += 1

error_bars = np.array(error_bars)

pylab.errorbar(np.arange(len(error_bars))+1, error_means, yerr=error_bars.T, color='k', linewidth=3)

import scipy.stats
for i, j in [(0,1), (0,2), (1,2)]:
    print i, j, scipy.stats.ttest_ind(all_data[i], all_data[j])[1]

pylab.xticks([1, 2, 3], ['Intel i5-337U CPU\n(5200 neurons)', 'Nvidia Tesla C2075 GPU\n(1500 neurons)', 'SpiNNaker core\n(500 neurons)'])

def annotate_bar(ax, text, x1, x2, y, text_offset, shrink=50):
    ax.annotate(text, xy=((x1+x2)*0.5, y+text_offset), ha='center')
    props = dict(connectionstyle='bar', arrowstyle='-', shrinkA=shrink, 
                 shrinkB=shrink, lw=2)
    ax.annotate('', xy=(x1,y), xytext=(x2, y), arrowprops=props)

annotate_bar(ax, 'p>0.05', 1, 3, 0.019, 0.017, shrink=105)
annotate_bar(ax, '', 1, 1.9, 0.025, 0.04, shrink=45)
annotate_bar(ax, '', 2.1, 3, 0.025, 0.04, shrink=45)


pylab.title('Computational Power Benchmark')
pylab.ylabel('rmse')
pylab.ylim(0, 0.04)
pylab.savefig('plot_compute.png', dpi=100)
#pylab.show()
