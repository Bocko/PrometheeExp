import numpy as np
import multiprocessing as mp
import itertools
import time

possible_weights = np.linspace(0, 1, 6)
crit_nb = 7

def sum1(l):
    return sum(l) == 1

def pool_filter(p, func, l):
    return [c for c, keep in zip(l, p.imap(func, l, chunksize=1024)) if keep]

p = mp.Pool(4)
tic = time.time()
w1 = itertools.product(possible_weights, repeat=crit_nb)
wc1 = [c for c in w1 if sum(c) == 1]
print(len(wc1))
print(time.time()-tic)
tic = time.time()
w2 = itertools.product(possible_weights, repeat=crit_nb)
wc2 = pool_filter(p, sum1, w2)
print(len(wc2))
print(time.time()-tic)

p.close()
p.join()