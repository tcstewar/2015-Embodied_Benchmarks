from benchmark_min import AdaptiveControl

import numpy as np
rng = np.random.RandomState()

for i in range(40):
    AdaptiveControl().run(no_figs=True, T=20, seed=i, max_freq=1,
                scale_add=1, delay=rng.uniform(0, 0.04),
                filter=rng.uniform(0, 0.01),
                noise=rng.uniform(0, 0.1),
                adapt=True, data_dir='vary_delay')
