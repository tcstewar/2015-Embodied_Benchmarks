import time

import nengo
import numpy as np


from system import System
from random_signal import Signal
from pid import PID
import benchmark

class AdaptiveControl(benchmark.Benchmark):
    def params(self):
        self.default('Kp', Kp=2.0)
        self.default('Kd', Kd=1.0)
        self.default('Ki', Ki=0.0)
        self.default('tau_d', tau_d=0.001)
        self.default('T', T=10.0)
        self.default('path', path='random')
        self.default('period', period=4.0)
        self.default('use adaptation', adapt=False)
        self.default('n_neurons', n_neurons=500)
        self.default('learning rate', learning_rate=1.0)
        self.default('max_freq', max_freq=1.0)
        self.default('synapse', synapse=0.01)
        self.default('radius', radius=1.0)
        self.default('number of dimensions', D=1)
        self.default('scale_add', scale_add=1)
        self.default('noise', noise=0.1)
        self.default('filter', filter=0.01)
        self.default('delay', delay=0.01)

    def model(self, p):

        model = nengo.Network()
        with model:

            system = System(p.D, p.D, dt=p.dt, seed=p.seed,
                    motor_noise=p.noise, sense_noise=p.noise,
                    scale_add=p.scale_add,
                    motor_scale=10,
                    motor_delay=p.delay, sensor_delay=p.delay,
                    motor_filter=p.filter, sensor_filter=p.filter)

            def minsim_system(t, x):
                return system.step(x)

            minsim = nengo.Node(minsim_system, size_in=p.D, size_out=p.D*2)

            pid = PID(p.Kp, p.Kd, p.Ki, tau_d=p.tau_d)
            control = nengo.Node(lambda t, x: pid.step(x[:p.D], x[p.D:]),
                                 size_in=p.D*2)
            nengo.Connection(minsim[:p.D], control[:p.D], synapse=0)
            nengo.Connection(control, minsim, synapse=None)

            if p.adapt:
                adapt = nengo.Ensemble(p.n_neurons, dimensions=p.D*2,
                                       radius=p.radius)
                nengo.Connection(minsim, adapt, synapse=None)
                conn = nengo.Connection(adapt, minsim, synapse=p.synapse,
                        function=lambda x: [0]*p.D,
                        learning_rule_type=nengo.PES())
                conn.learning_rule_type.learning_rate *= p.learning_rate
                nengo.Connection(control, conn.learning_rule, synapse=None,
                        transform=-1)
                        
            if p.path == 'random':
                signal = Signal(p.D, p.period, dt=p.dt, max_freq=p.max_freq, seed=p.seed)
                def desired_func(t):
                    return signal.value(t) * np.pi / 2

            elif p.path == 'step':
                def desired_func(t):
                    t = (t % p.period) / p.period
                    if 0.25 < t < 0.5:
                        return -np.pi / 2, -np.pi / 2
                    elif 0.75 < t < 1.0:
                        return np.pi / 2, np.pi / 2
                    else:
                        return 0, 0
            
            desired = nengo.Node(desired_func)
            nengo.Connection(desired, control[p.D:], synapse=None)

            self.p_desired = nengo.Probe(desired, synapse=None)
            self.p_q = nengo.Probe(minsim, synapse=None)
            self.p_u = nengo.Probe(control, synapse=None)
        return model

    def evaluate(self, p, sim, plt):
        #start_time = time.time()
        #while time.time() - start_time < p.T:
        #    sim.run(p.dt, progress_bar=False)
        sim.run(p.T)

        q = sim.data[self.p_q][:,0]
        d = sim.data[self.p_desired][:,0]
        t = sim.trange()

        N = len(q) / 2

        # find an offset that lines up the data best (this is the delay)
        offsets = []
        for i in range(p.D):
            q = sim.data[self.p_q][:,i]
            d = sim.data[self.p_desired][:,i]
            offset = benchmark.find_offset(q[N:], d[N:])
            if offset == 0:
                offset = 1
            offsets.append(offset)
        offset = int(np.mean(offsets))
        delay = p.dt * offset

        if plt is not None:
            plt.plot(t[offset:], d[:-offset], label='$q_d$')
            #plt.plot(t[offset:], d[offset:])
            plt.plot(t[offset:], q[offset:], label='$q$')
            plt.legend(loc='upper left')

            #plt.plot(np.correlate(d, q, 'full')[len(q):])

        diff = sim.data[self.p_desired][:-offset] - sim.data[self.p_q][offset:][:,:p.D]

        diff = diff[N:]
        rmse = np.sqrt(np.mean(diff.flatten()**2))


        return dict(delay=delay, rmse=rmse)

if __name__ == '__main__':
    AdaptiveControl().run()

