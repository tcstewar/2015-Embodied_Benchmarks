import time

import nengo
import numpy as np


from system import System
from random_signal import Signal
from pid import PID
import benchmark

class ZeroDecoder(nengo.solvers.Solver):
    weights = False
    def __call__(self, A, Y, rng=None, E=None):
        return np.zeros((A.shape[1], Y.shape[1]), dtype=float), []

class AdaptiveControl(benchmark.Benchmark):
    def params(self):
        self.default('Kp', Kp=2.0)
        self.default('Kd', Kd=1.0)
        self.default('Ki', Ki=0.0)
        self.default('tau_d', tau_d=0.001)
        self.default('T', T=10.0)
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

            self.system_state = []
            self.system_times = []
            self.system_desired = []
            def minsim_system(t, x):
                r = system.step(x)
                self.system_state.append(system.state)
                self.system_times.append(t)
                self.system_desired.append(signal.value(t))
                return r

            minsim = nengo.Node(minsim_system, size_in=p.D, size_out=p.D)

            state_node = nengo.Node(lambda t: system.state)

            pid = PID(p.Kp, p.Kd, p.Ki, tau_d=p.tau_d)
            control = nengo.Node(lambda t, x: pid.step(x[:p.D], x[p.D:]),
                                 size_in=p.D*2)
            nengo.Connection(minsim, control[:p.D], synapse=0)
            nengo.Connection(control, minsim, synapse=None)

            if p.adapt:

                adapt = nengo.Ensemble(p.n_neurons, dimensions=p.D,
                                       radius=p.radius)
                nengo.Connection(minsim, adapt, synapse=None)
                conn = nengo.Connection(adapt, minsim, synapse=p.synapse,
                        function=lambda x: [0]*p.D,
                        solver=ZeroDecoder(),
                        learning_rule_type=nengo.PES())
                conn.learning_rule_type.learning_rate *= p.learning_rate
                nengo.Connection(control, conn.learning_rule, synapse=None,
                        transform=-1)

            signal = Signal(p.D, p.period, dt=p.dt, max_freq=p.max_freq, seed=p.seed)
            desired = nengo.Node(signal.value)
            nengo.Connection(desired, control[p.D:], synapse=None)

            #self.p_desired = nengo.Probe(desired, synapse=None)
            #self.p_q = nengo.Probe(state_node, synapse=None)
        return model

    def evaluate(self, p, sim, plt):
        #start_time = time.time()
        #while time.time() - start_time < p.T:
        #    sim.run(p.dt, progress_bar=False)
        sim.run(p.T)

        #q = sim.data[self.p_q][:,0]
        q = np.array(self.system_state)[:,0]
        d = np.array(self.system_desired)[:,0]
        t = np.array(self.system_times)

        N = len(q) / 2

        # find an offset that lines up the data best (this is the delay)
        offsets = []
        for i in range(p.D):
            #q = sim.data[self.p_q][:,i]
            q = np.array(self.system_state)[:,i]
            d = np.array(self.system_desired)[:,i]
            offset = benchmark.find_offset(q[N:], d[N:])
            if offset == 0:
                offset = 1
            offsets.append(offset)
        offset = int(np.mean(offsets))

        delay = np.mean(t[offset:]-t[:-offset])
        spinn_dt = np.mean(t[1:]-t[:-1])

        if plt is not None:
            plt.plot(t[offset:], d[:-offset], label='$q_d$')
            #plt.plot(t[offset:], d[offset:])
            t2 = self.system_times
            plt.plot(t2[offset:], q[offset:], label='$q$')
            plt.legend(loc='upper left')

            #plt.plot(np.correlate(d, q, 'full')[len(q):])


        diff = np.array(self.system_desired)[:-offset] - np.array(self.system_state)[offset:]
        diff = diff[N:]
        rmse = np.sqrt(np.mean(diff.flatten()**2))


        return dict(delay=delay, rmse=rmse, spinn_dt=spinn_dt)

if __name__ == '__main__':
    AdaptiveControl().run()

