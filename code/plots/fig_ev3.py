import pylab
import matplotlib
import shelve
import numpy as np

pylab.figure(figsize=(10,6))

def find_offset(a, b):
    assert len(a) == len(b)
    corr = np.correlate(a, b, 'full')
    index = np.argmax(corr[len(a):])
    return index

index = 0
for path in ['step', 'random']:
    for adapt in ['False', 'True']:

        db = shelve.open('SingleArmEV3#path=%s,adapt=%s.db' % (path, adapt))

        index += 1
        pylab.subplot(2, 2, index)

        t = db['p_t'][:,0]
        q = db['p_q'][:,0]
        d = db['p_desired'][:,0]

        if path == 'random':
            q *= 2
            d *= 2

        pylab.plot(t, q, color='#888888', linewidth=2, label='$q$')
        pylab.plot(t, d, color='k', linewidth=1, label='$q_d$')

        if path == 'step':
            pylab.gca().add_patch(matplotlib.patches.Ellipse(xy=(7.5, 1.7), width=2, height=0.5, edgecolor='k', fc='None', lw=2))
            pylab.gca().add_patch(matplotlib.patches.Ellipse(xy=(5.5, -1.7), width=2, height=0.5, edgecolor='k', fc='None', lw=2))
        if path == 'random':
            pylab.gca().add_patch(matplotlib.patches.Ellipse(xy=(7.7, 1.6), width=2, height=0.5, edgecolor='k', fc='None', lw=2))
            pylab.gca().add_patch(matplotlib.patches.Ellipse(xy=(8.5, -1.6), width=2, height=0.5, edgecolor='k', fc='None', lw=2))

        '''

        error = np.abs(q-d)
        cum_error = np.cumsum(error)
        print max(cum_error)
        pylab.plot(t, cum_error/300)

        offset = find_offset(q, d)
        print offset
        pylab.plot(t[offset:], q[offset:] - d[:-offset])

        offset=1
        diff = q[offset:] - d[:-offset]
        #diff = diff[len(diff)/2:]
        rmse = np.sqrt(np.mean(diff.flatten()**2))
        pylab.text(5, 0.5, 'rmse=%1.3f' % rmse)
        '''

        pylab.ylim(-2, 2)
        pylab.yticks([-np.pi/2, 0, np.pi/2], ['$-\pi/2$', '0','$\pi/2$'])

        if adapt == 'False':
            pylab.ylabel('joint angle (radians)')
        if path == 'random':
            pylab.xlabel('time (s)')
        if path == 'step' and adapt=='False':
            pylab.title('without adaptation')
        if path == 'step' and adapt=='True':
            pylab.title('with adaptation')

        pylab.legend(loc='upper left')




        db.close()

pylab.savefig('fig_ev3.png', dpi=600)
#pylab.show()


