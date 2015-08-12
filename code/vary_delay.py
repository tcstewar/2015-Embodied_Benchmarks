from benchmark_min import AdaptiveControl

import numpy as np
rng = np.random.RandomState()

for i in range(10):
    AdaptiveControl().run(no_figs=True, T=20, seed=i, max_freq=1,
                scale_add=1, delay=rng.uniform(0, 0.04),
                adapt=True, data_dir='vary_delay')
