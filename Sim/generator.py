#!/usr/bin/env python3

import argparse
import numpy as np
import itertools
# import testproblem
import csv_file
from promethee import *
import multiprocessing
import time
import re
import pickle

def parse_args():
    parser = argparse.ArgumentParser(description = 'Promethee Expressivity')

    parser.add_argument('-s','--step', nargs=1, type=float, required=True)
    parser.add_argument('-i', '--input', nargs=1, type=str, required=True)
    # parser.add_argument('-t','--stability', nargs=1, type=int)

    parser.add_argument('-o','--output', nargs=1)

    #parser.add_argument('dot_graph', nargs=1, type=str, required=True)
    #parser.add_argument('-p','--physical', nargs=1, required=True)
    #parser.add_argument('-v','--virtual', nargs=1, required=True)

    args = parser.parse_args()
    return args

def weights_choice(step):
    start = 0
    stop = 1
    np_step = 1 / step + 1

    return np.linspace(start,stop,np_step)

def generate_all_weights(possible_weights, crit_nb):
    all_weights = [seq for seq in itertools.product(possible_weights, repeat=crit_nb) if sum(seq) == 1]
    return all_weights

def generate_all_weights2(alt_eval, possible_weights, func_pref_crit, alt_names):
    crit_nb = len(func_pref_crit)
    all_weights = [(alt_eval, seq, func_pref_crit, alt_names) for seq in itertools.product(possible_weights, repeat=crit_nb) if sum(seq) == 1]
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

def generate_all_rankings2(pool, all_weights, func_pref_crit, alt_names, alt_eval):
    crit_nb = len(func_pref_crit)
    all_rankings = pool.map(par_ranking_eval2, all_weights)

    return all_rankings

def filter_unique_rankings(all_rankings, stability_level=0):
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

def main():
    args = parse_args()
    if args.step[0] > 0:
        step = args.step[0]
    else:
        raise('Please enter positive step value')

    print("Simulation data:")
    # Loading problem
    if args.input[0] == 'test':
        criteria_names, original_weights, func_pref_crit, alt_names, alt_eval = testproblem.subset_bestcities()
        print("Problem:", "test")
    elif args.input[0] == 'epi2016':
        criteria_names, original_weights, func_pref_crit, alt_names, alt_eval = testproblem.epi2016()
        print("Problem:", "epi2016")
    else:
        raise('Please use "test" or "epi2016" for now...')

    # if args.stability != None:
    #     stability_level = args.stability[0]
    # else:
    #     stability_level = 1
    # print("Stability level:", stability_level)
    
    # lin_spacing = [3, 5, 9, 11, 17, 21, 41, 101]
    possible_weights = weights_choice(step)
    print("Possible weights:", possible_weights)

    if args.output != None:
        filename = args.output[0]
        print("Savefile:", filename)

    crit_nb = len(criteria_names)
    
    pool = multiprocessing.Pool(8)
    # all_weights = generate_all_weights(possible_weights, crit_nb)
    libname = "lib/step_" + re.sub("[^0-9]", "", str(step)) + "_" + str(crit_nb) + ".sav"
    try:    
        all_weights = pickle.load(open(libname, "rb" ))
        print("Found file for step " + str(step) + ":", libname)
        start = input("Start? y/[n]: ")
        if start.upper() != "Y":
            return 0
        tic = time.time()
    except:
        print("File for step not found!")
        start = input("Start? y/[n]: ")
        if start.upper() != "Y":
            return 0
        tic = time.time()
        all_weights = generate_all_weights2(alt_eval, possible_weights, func_pref_crit, alt_names)
        pickle.dump(all_weights, open(libname,'wb'),pickle.HIGHEST_PROTOCOL)
    print(time.time()-tic)
    # unique_rankings = generate_all_rankings(all_weights, func_pref_crit, alt_names, alt_eval, stability_level=stability_level)
    all_rankings = generate_all_rankings2(pool, all_weights, func_pref_crit, alt_names, alt_eval)
    # unique_rankings = filter_unique_rankings(all_rankings, stability_level=stability_level)
    # tic = time.time()
    # unique_rankings = par_generate_all_rankings(pool, func_pref_crit, alt_names, alt_eval, stability_level=1)
    print(time.time()-tic)
    # print(len(unique_rankings))

    pool.close()
    pool.join()

    if args.output != None:
        pickle.dump([possible_weights, all_rankings], open(filename,'wb'),pickle.HIGHEST_PROTOCOL)

if __name__ == "__main__":
    main()
