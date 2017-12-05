import numpy as np
import multiprocessing as mp
import itertools

alphabet = np.linspace(0, 1, 11)
num_parts = 6
part_size = len(alphabet) // num_parts

def do_job(first_bits):
    res = []
    for x in itertools.product(first_bits, alphabet, alphabet, alphabet, alphabet, alphabet):
        res.append(x)
    return res

def main():
    pool = mp.Pool(4)
    results = []
    for i in range(num_parts):
        if i == num_parts - 1:
            first_bit = alphabet[part_size * i :]
        else:
            first_bit = alphabet[part_size * i : part_size * (i+1)]
        results.append(pool.apply_async(do_job(first_bit)))

    pool.close()
    pool.join()
    # results = [r.get() for r in results]
    return results

if __name__ == "__main__":
    results = main()
    # print(results)
    # for r in results:
    #     print(r)
