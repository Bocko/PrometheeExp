import numpy as np
import multiprocessing as mp
import itertools
import time

possible_weights = np.linspace(0, 1, 11)
crit_nb = 7

def sum1(l):
    return sum(l) == 1

def pool_filter(p, func, candidates):
    return [c for c, keep in zip(candidates, p.imap(func, candidates, chunksize=1024)) if keep]

p = mp.Pool(4)
tic = time.time()
w = itertools.product(possible_weights, repeat=crit_nb)
wc = [c for c in w if sum(c) == 1]
print(len(wc))
print(time.time()-tic)
tic = time.time()
w = itertools.product(possible_weights, repeat=crit_nb)
wc = pool_filter(p, sum1, w)
print(len(wc))
print(time.time()-tic)

p.close()
p.join()