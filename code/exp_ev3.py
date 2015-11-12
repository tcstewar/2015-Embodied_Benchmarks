from benchmark_ev3 import SingleArmEV3

import numpy as np
rng = np.random.RandomState()

start = 45

for i in range(start,start+5):
    for adapt in [False, True]:
        SingleArmEV3().run(no_figs=True, T=20, seed=i, max_freq=1,
                scale_add=1,
                n_neurons=500,
                adapt=adapt, 
                path='random',
                data_dir='ev3_%s' % adapt)
