import numpy as np
import itertools
# import testproblem
import csv_file
from promethee import *
import multiprocessing
import time

def generate_all_weights(possible_weights, crit_nb):
    all_weights = [seq for seq in itertools.product(possible_weights, repeat=crit_nb) if sum(seq) == 1]
    return all_weights

def generate_all_rankings(all_weights, func_pref_crit, alt_names, alt_eval, stability_level=0):
    crit_nb = len(func_pref_crit)

    unique_rankings = []
    for weights in all_weights:
        netflows = netflows_eval(alt_eval, weights, func_pref_crit)
        ranking, sorted_netflows = netflows_to_ranking(alt_names, netflows)
        if stability_level != 0:
            if ranking[:stability_level] not in unique_rankings:
                unique_rankings.append(ranking[:stability_level])
                print(ranking[:stability_level])

        else:
            if ranking not in unique_rankings:
                unique_rankings.append(ranking)

    return unique_rankings

def generate_all_rankings2(all_weights, func_pref_crit, alt_names, alt_eval, stability_level=0):
    crit_nb = len(func_pref_crit)
    pool.map(par_ranking_eval, all_weights)
    unique_rankings = []
    for weights in all_weights:
        if stability_level != 0:
            if ranking[:stability_level] not in unique_rankings:
                unique_rankings.append(ranking[:stability_level])
                print(ranking[:stability_level])

        else:
            if ranking not in unique_rankings:
                unique_rankings.append(ranking)

    return unique_rankings

# def sum_equal1(seq):
#     return sum(seq) == 1

# def par_generate_all_weights(pool, possible_weights, crit_nb, alt_eval, func_pref_crit, alt_names):
#     all_weights = itertools.product(possible_weights, repeat=crit_nb)
#     return [(alt_eval, w, func_pref_crit, alt_names) for w, keep in zip(all_weights, pool.imap(sum_equal1, all_weights)) if keep]

# def iter_generate_all_weights(pool, possible_weights, crit_nb, alt_eval, func_pref_crit, alt_names):
#     all_weights = itertools.filterfalse(lambda x: sum(x) != 1,itertools.product(possible_weights, repeat=crit_nb))
#     return [(alt_eval, w, func_pref_crit, alt_names) for w in all_weights]

def par_generate_all_rankings(pool, func_pref_crit, alt_names, alt_eval, stability_level=0):
    crit_nb = len(func_pref_crit)
    all_weights = itertools.filterfalse(lambda x: sum(x) != 1,itertools.product(possible_weights, repeat=crit_nb))
    all_rankings = pool.imap_unordered(par_ranking_eval, all_weights, chunksize=1024)

    unique_rankings = []
    for ranking, netflows in all_rankings:
        if stability_level != 0:
            if ranking[:stability_level] not in unique_rankings:
                unique_rankings.append(ranking[:stability_level])
                print(ranking[:stability_level])

        else:
            if ranking not in unique_rankings:
                unique_rankings.append(ranking)

    return unique_rankings


if __name__ == "__main__":
    pool = multiprocessing.Pool(4)
    # Load problem
    # criteria_names, original_weights, func_pref_crit, alt_names, alt_eval = testproblem.subset_bestcities()
    original_weights, criteria_names, alt_names, alt_eval = csv_file.open_csv('epi-2016.csv')
    func_pref_crit = [PreferenceType2(0), PreferenceType2(0), PreferenceType2(0), PreferenceType2(0), PreferenceType2(0), PreferenceType2(0), PreferenceType2(0), PreferenceType2(0), PreferenceType2(0)]
    lin_spacing = [3, 5, 9, 11, 17, 21, 41, 101]
    possible_weights = np.linspace(0, 1, 5)
    crit_nb = len(criteria_names)
    tic = time.time()
    all_weights = generate_all_weights(possible_weights, crit_nb)
    print(time.time()-tic)
    unique_rankings = generate_all_rankings2(all_weights, func_pref_crit, alt_names, alt_eval, stability_level=1)
    # tic = time.time()
    # unique_rankings = par_generate_all_rankings(pool, func_pref_crit, alt_names, alt_eval, stability_level=1)
    print(time.time()-tic)
    print(len(unique_rankings))

    pool.close()
    pool.join()