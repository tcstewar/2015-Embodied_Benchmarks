import os
import sys
import bootstrapci

import numpy as np
import pylab

fig = pylab.figure(figsize=(6,5))
ax = fig.add_subplot(1,1,1)

do_logx = False

error_bars = []
error_means = []
index = 1
for adapt in [False, True]:
    path = 'ev3_%s' % adapt

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

            x = d['_adapt']
            y = d['rmse']

            if do_logx:
                x = np.log2(x)

            data_x.append(x)
            data_y.append(y)
            print x, y

    #data_x = data_x[:30]
    #data_y = data_y[:30]

    data_x = np.array(data_x)
    data_y = np.array(data_y)


    mean = np.mean(data_y)
    sd = np.std(data_y)
    ci = bootstrapci.bootstrapci(data_y, np.mean)

    width = 0.3

    pylab.fill_between([index-width, index+width], mean-sd, mean+sd, color='#aaaaaa')
    pylab.scatter(np.random.uniform(index-width, index+width, data_y.shape), data_y, s=30, marker='x', color='k', alpha=0.3)
    error_means.append(mean)
    error_bars.append([mean-ci[0], ci[1]-mean])
    index += 1

error_bars = np.array(error_bars)

pylab.errorbar(np.arange(len(error_bars))+1, error_means, yerr=error_bars.T, color='k', linewidth=3, capthick=2, capsize=4)

pylab.xticks([1, 2], ['without adaptation', 'with adaptation\n(500 neurons)'])

def annotate_bar(ax, text, x1, x2, y, text_offset, shrink=50):
    ax.annotate(text, xy=((x1+x2)*0.5, y+text_offset), ha='center')
    props = dict(connectionstyle='bar', arrowstyle='-', shrinkA=shrink, 
                 shrinkB=shrink, lw=2)
    ax.annotate('', xy=(x1,y), xytext=(x2, y), arrowprops=props)

#annotate_bar(ax, 'p<0.05', 1, 3, 0.14, 0.08, shrink=80)
#annotate_bar(ax, '', 2, 4, 0.135, 0, shrink=80)
#annotate_bar(ax, 'p>0.05', 2, 4, 0, 0.08, shrink=80)
#annotate_bar(ax, '', 2, 2.9, 0.03, 0.04, shrink=35)
#annotate_bar(ax, '', 3.1, 4, 0.03, 0.04, shrink=35)

pylab.ylabel('rmse (radians)')
pylab.ylim(0, 0.12)
pylab.savefig('plot_ev3.png', dpi=300)
pylab.show()
