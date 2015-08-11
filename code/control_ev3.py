import time

import nengo
import numpy as np
import ev3link
import embodied_benchmarks as bench

link = ev3link.EV3Link('10.42.0.3')

path0 = '/sys/class/tacho-motor/motor0/'
link.write(path0 + 'command', 'run-direct')
link.write(path0 + 'position', '0')
print 'current position: ', link.read(path0 + 'position')
    
start_time = time.time()
    
model = nengo.Network()
with model:
    
    def ev3_system(t, x):
        value = int(100 * x[0])
        if value > 100:
            value = 100
        if value < -100:
            value = -100
        value = '%d' % value
        link.write(path0 + 'duty_cycle_sp', value)
        p = link.read(path0 + 'position')
        try:
            return float(p) / 180 * np.pi
        except:
            return 0
    
    ev3 = nengo.Node(ev3_system, size_in=1, size_out=1)
    
    pid = bench.pid.PID(2,1,0, tau_d=0.001)
    control = nengo.Node(lambda t, x: pid.step(x[:1], x[1:]), size_in=2)
    nengo.Connection(ev3, control[:1], synapse=0)
    nengo.Connection(control, ev3, synapse=None)
    
    actual_time = nengo.Node(lambda t: time.time() - start_time)

    def desired_func(t, actual_t):
        return np.sin(actual_t*2*np.pi)
    desired = nengo.Node(desired_func, size_in=1)
    nengo.Connection(actual_time, desired, synapse=None)
    nengo.Connection(desired, control[1:], synapse=None)

    p_desired = nengo.Probe(desired, synapse=None)
    p_q = nengo.Probe(ev3, synapse=None)
    p_t = nengo.Probe(actual_time, synapse=None)



sim = nengo.Simulator(model)
start_time = time.time()
sim.run(0.1)
    
link.write(path0 + 'duty_cycle_sp', '0')

import pylab
pylab.plot(sim.data[p_t], sim.data[p_desired])
pylab.plot(sim.data[p_t], sim.data[p_q])
pylab.show()
    
