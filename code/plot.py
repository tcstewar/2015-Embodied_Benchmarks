import shelve
import sys

import numpy as np
import pylab

db = shelve.open(sys.argv[1])

q = db['p_q'][:,0]
d = db['p_desired'][:,0]
t = db['p_t']

def find_offset(a, b):
    assert len(a) == len(b)
    corr = np.correlate(a, b, 'full')
    index = np.argmax(corr[len(a):])
    return index

offset = find_offset(q, d)

dt = np.mean(t[offset:]-t[:-offset])
print dt

#pylab.plot(t, d)
pylab.plot(t[offset:], d[:-offset])
pylab.plot(t[offset:], q[offset:])
pylab.show()
