import time

import nengo
import numpy as np
import ev3link
import embodied_benchmarks as bench

import benchmark

class SingleArmEV3(benchmark.Benchmark):
    def params(self):
        self.default('Kp', Kp=2.0)
        self.default('Kd', Kd=1.0)
        self.default('Ki', Ki=0.0)
        self.default('tau_d', tau_d=0.001)
        self.default('T', T=0.5)
        self.default('IP address of EV3', address='10.42.0.3')
        self.default('motor index', motor_index=0)
        self.default('desired path', path='step')
        self.default('period', period=4.0)
        self.default('use adaptation', adapt=False)
        self.default('n_neurons', n_neurons=500)
        self.default('learning rate', learning_rate=1.0)
        self.default('max_freq', max_freq=1.0)
        self.default('synapse', synapse=0.01)
        self.default('radius', radius=1.0)

    def model(self, p):
        link = ev3link.EV3Link(p.address)
        self.link = link
        path = '/sys/class/tacho-motor/motor%d/' % p.motor_index
        self.path = path
        link.write(path + 'command', 'stop')
        link.write(path + 'position', '0\n')
        link.write(path + 'command', 'run-direct')
        print 'current position: ', link.read(path + 'position')
    
        model = nengo.Network()
        with model:
            
            def ev3_system(t, x):
                value = int(100 * x[0])
                if value > 100:
                    value = 100
                if value < -100:
                    value = -100
                value = '%d' % value
                link.write(path + 'duty_cycle_sp', value)
                p = link.read(path + 'position')
                try:
                    return float(p) / 180 * np.pi
                except:
                    return 0
            
            ev3 = nengo.Node(ev3_system, size_in=1, size_out=1)
            
            #if p.adapt:
            #    pid = bench.pid.PDAdapt(1, p.Kp, p.Kd, tau_d=p.tau_d, learning_rate=p.learning_rate,
            #                            n_neurons=p.n_neurons)
            pid = bench.pid.PID(p.Kp, p.Kd, p.Ki, tau_d=p.tau_d)
            control = nengo.Node(lambda t, x: pid.step(x[:1], x[1:]), size_in=2)
            nengo.Connection(ev3, control[:1], synapse=0)
            nengo.Connection(control, ev3, synapse=None)

            if p.adapt:
                adapt = nengo.Ensemble(p.n_neurons, dimensions=1, radius=p.radius)
                nengo.Connection(ev3, adapt, synapse=None)
                conn = nengo.Connection(adapt, ev3, synapse=p.synapse,
                        function=lambda x: 0,
                        learning_rule_type=nengo.PES())
                conn.learning_rule_type.learning_rate *= p.learning_rate
                nengo.Connection(control, conn.learning_rule, synapse=None,
                        transform=-1)
            
            actual_time = nengo.Node(lambda t: time.time() - self.start_time,
                    size_in=0, size_out=1)

            if p.path == 'sin':
                def desired_func(t, actual_t):
                    return np.sin(actual_t*2*np.pi / p.period) * np.pi / 2
            elif p.path == 'step':
                def desired_func(t, actual_t):
                    t = (actual_t % p.period) / p.period
                    if 0.25 < t < 0.5:
                        return -np.pi / 2
                    elif 0.75 < t < 1.0:
                        return np.pi / 2
                    else:
                        return 0
            elif p.path == 'random':
                signal = bench.signal.Signal(1, p.period, dt=p.dt, max_freq=p.max_freq, seed=p.seed)
                def desired_func(t, actual_t):
                    return signal.value(actual_t) * np.pi / 2

            desired = nengo.Node(desired_func, size_in=1)
            nengo.Connection(actual_time, desired, synapse=None)
            nengo.Connection(desired, control[1:], synapse=None)

            self.p_desired = nengo.Probe(desired, synapse=None)
            self.p_q = nengo.Probe(ev3, synapse=None)
            self.p_t = nengo.Probe(actual_time, synapse=None)
            self.p_u = nengo.Probe(control, synapse=None)
        return model

    def evaluate(self, p, sim, plt):
        start_time = time.time()
        while time.time() - start_time < p.T:
            sim.run(p.dt, progress_bar=False)
        #sim.run(p.T)
    
        self.link.write(self.path + 'duty_cycle_sp', '0')

        if plt is not None:
            plt.plot(sim.data[self.p_t], sim.data[self.p_desired])
            plt.plot(sim.data[self.p_t], sim.data[self.p_q])
            #plt.plot(sim.data[self.p_t], sim.data[self.p_u])

        rate = len(sim.data[self.p_t]) / p.T

        q = sim.data[self.p_q][:,0]
        d = sim.data[self.p_desired][:,0]
        t = sim.data[self.p_t][:,0]
        
        offset = benchmark.find_offset(q, d)

        delay = np.mean(t[offset:]-t[:-offset])

        diff = d[:-offset] - q[offset:]
        rmse = np.sqrt(np.mean(diff**2))


        return dict(rate=rate, delay=delay, rmse=rmse)
    
if __name__ == '__main__':
    SingleArmEV3().run()

