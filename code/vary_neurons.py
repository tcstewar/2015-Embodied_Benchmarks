from benchmark_min import AdaptiveControl
import traceback

import numpy as np
rng = np.random.RandomState()

for i in range(100):
    try:
        AdaptiveControl().run(no_figs=True, seed=i, max_freq=1,
                    scale_add=1, delay=rng.uniform(0, 0.01),
                    D=15, T=60,
                    filter=rng.uniform(0, 0.01),
                    noise=rng.uniform(0, 0.1),
                    n_neurons=int(2.0**rng.uniform(0,10)),
                    adapt=True,
                    data_dir='vary_neuronsD15')
    except:
        traceback.print_exc()
