from benchmark_min_spinn import AdaptiveControl
import traceback

import numpy as np
rng = np.random.RandomState()

for i in range(100):
    for D in [1, 5, 10, 15]:
        try:
            AdaptiveControl().run(no_figs=True, seed=i, max_freq=1,
                        scale_add=1, delay=rng.uniform(0, 0.01),
                        D=D, T=60,
                        filter=rng.uniform(0, 0.01),
                        noise=rng.uniform(0, 0.1),
                        n_neurons=int(2.0**rng.uniform(0,10)),
                        adapt=True,
                        debug=True,
                        backend='nengo_spinnaker',
                        data_dir='vary_neuronsD%d_spinn' % D)
        except:
            traceback.print_exc()
