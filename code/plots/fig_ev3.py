import pylab
import shelve
import numpy as np

pylab.figure(figsize=(10,6))

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
        pylab.ylim(-2, 2)
        pylab.yticks([-np.pi/2, 0, np.pi/2], ['$-\pi$', '0','$\pi$'])

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
pylab.show()


