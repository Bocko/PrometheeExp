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
import os
import weights_generator as wg

LIB_DIR = 'lib'

def parse_args():
    parser = argparse.ArgumentParser(description = 'Promethee Expressivity')

    parser.add_argument('-s','--step', nargs=1, type=float)
    parser.add_argument('-i', '--input', nargs=1, type=str, required=True)
    parser.add_argument('-m', '--multiplier', nargs=1, type=int)
    parser.add_argument('-c', '--chunk_size', nargs=1, type=int)
    parser.add_argument('-d', '--method', nargs=1, type=str, required=True)
    parser.add_argument('-a', '--statonly', nargs='*', default=False)
    parser.add_argument('-r', '--randomweights', nargs=1, type=int)
    # parser.add_argument('-t','--stability', nargs=1, type=int)

    parser.add_argument('-o','--output', nargs=1)

    args = parser.parse_args()
    return args

def weights_choice(step):
    start = 0
    stop = 1
    np_step = int(1 / step + 1)

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

def sum_equal1(seq):
    return sum(seq) == 1

def par_generate_all_weights(pool, alt_eval, possible_weights, func_pref_crit, alt_names):
    crit_nb = len(func_pref_crit)
    all_weights = itertools.product(possible_weights, repeat=crit_nb)
    return [(alt_eval, seq, func_pref_crit, alt_names) for seq, keep in zip(all_weights, pool.imap(sum_equal1, all_weights, chunksize=1024)) if keep]

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

def maut_ranking(args):
    alt_eval, alt_names, weights = args
    prod = np.sum(np.array(alt_eval) * weights, axis=1)
    ranking = []
    score = []
    for i in sorted(enumerate(prod), key=lambda x: x[1], reverse=True):
        ranking.append(alt_names[i[0]])
        score.append(i[1])

    return ranking, score

def generate_all_maut_rankings(pool, all_weights):
    all_rankings = pool.map(maut_ranking, all_weights)
    return all_rankings

def maut_distrib(args):
    distrib, alt_eval, alt_names, weights = args
    prod = np.sum(np.array(alt_eval) * weights, axis=1)
    ranking = []
    score = []
    for i in sorted(enumerate(prod), key=lambda x: x[1], reverse=True):
        ranking.append(alt_names[i[0]])
        score.append(i[1])

    tranking = tuple(ranking)
    distrib[tranking] = distrib.get(tranking,0) + 1

def generate_all_maut_distrib(pool, alt_eval, alt_names, all_weights):
    distrib = {}
    for w in range(len(all_weights)):
        prod = np.sum(np.array(alt_eval) * all_weights[w], axis=1)
        ranking = []
        score = []
        for i in sorted(enumerate(prod), key=lambda x: x[1], reverse=True):
            ranking.append(alt_names[i[0]])
            score.append(i[1])

        tranking = tuple(ranking)
        distrib[tranking] = distrib.get(tranking,0) + 1
        print(w+1, "/", len(all_weights))
        os.system('clear')
    return distrib

def weights_generator_recurs(alt_eval, int_possible_weights, func_pref_crit, alt_names, int_multiplier, w_sum, result, index):
    crit_nb = len(func_pref_crit)
    if index > crit_nb or w_sum < 0:
        return

    if index == crit_nb:
        if w_sum == 0:
            # print(result[:n])
            yield (alt_eval, np.array(result[:crit_nb]) / int_multiplier, func_pref_crit, alt_names)
            # yield np.array(result[:crit_nb]) / int_multiplier

        return

    for val in int_possible_weights:
        result[index] = val
        result.append(0)
        yield from weights_generator_recurs(alt_eval, int_possible_weights, func_pref_crit, alt_names, int_multiplier, w_sum-val, result, index + 1) 

def weights_generator(pool, alt_eval, possible_weights, func_pref_crit, alt_names, int_multiplier, w_sum):
    int_possible_weights = (possible_weights * int_multiplier).astype(int)
    for val in int_possible_weights:
        result = [val]
        result.append(0)
        yield from weights_generator_recurs(alt_eval, int_possible_weights, func_pref_crit, alt_names, int_multiplier, w_sum-val, result, 1)

def list_lib(libname):
    libnames = os.listdir(LIB_DIR)
    for i in range(len(libnames)-1,-1,-1):
        if libname not in libnames[i]:
            libnames.pop(i)

    return libnames

def main():
    args = parse_args()

    if (args.step == None and args.randomweights == None) or (args.step != None and args.randomweights != None):
        print("Error: use either step or randomweights")
        return

    if args.randomweights != None:
        randomweights = args.randomweights[0]
        print("Random generation of weights:", randomweights)
    else:
        randomweights = 0
        if args.step[0] > 0:
            step = args.step[0]
        else:
            print("Error: please enter positive step value")
            return

    if args.statonly == []:
        statonly = True
        print("Distribution only")
    else:
        statonly = False

    print("Simulation data:")
    # Loading problem
    if args.input[0] == 'test':
        criteria_names, original_weights, func_pref_crit, alt_names, alt_eval = testproblem.subset_bestcities()
        print("Problem:", "test")
    elif args.input[0] == 'epi2016':
        criteria_names, original_weights, func_pref_crit, alt_names, alt_eval = testproblem.epi2016()
        print("Problem:", "epi2016")
    elif args.input[0] == 'hdi2016':
        criteria_names, original_weights, func_pref_crit, alt_names, alt_eval = testproblem.hdi2016()
        print("Problem:", "hdi2016")
    elif args.input[0] == 'studentcities2017':
        criteria_names, original_weights, func_pref_crit, alt_names, alt_eval = testproblem.studentcities2017()
        print("Problem:", "studentcities2017")
    elif args.input[0] == 'safecities2017':
        criteria_names, original_weights, func_pref_crit, alt_names, alt_eval = testproblem.safecities2017()
        print("Problem:", "safecities2017")
    elif args.input[0] == 'gfsi2017':
        criteria_names, original_weights, func_pref_crit, alt_names, alt_eval = testproblem.foodsecurity2017()
    elif args.input[0] == 'di2017':
        criteria_names, original_weights, func_pref_crit, alt_names, alt_eval = testproblem.democracy2017()
    else:
        raise("Please use 'test', 'epi2016', 'hdi2016' for now...")

    if args.multiplier != None:
        int_multiplier = args.multiplier[0]
    else:
        int_multiplier = 100
    
    if args.randomweights == None:
        possible_weights = weights_choice(step)
        print("Possible weights:", possible_weights)
        int_possible_weights = (possible_weights * int_multiplier).astype(int)

    if args.chunk_size != None:
        chunk_size = args.chunk_size[0]
    else:
        chunk_size = 0
    chunk_id = [0]

    print("Chunk size:", chunk_size)

    crit_nb = len(criteria_names)
    print("Number of criteria:", crit_nb)

    if args.output != None:
        filename = args.output[0]
        print("Savefile:", filename)

    promethee_flag = False
    maut_flag = False
    if args.method[0].lower() == "promethee":
        promethee_flag = True
        print("Method: PROMETHEE II")
    elif args.method[0].lower() == "maut":
        maut_flag = True
        print("Method: MAUT")
    
    pool = multiprocessing.Pool(8)

    if chunk_size != 0:
        if args.output == None:
            print("Error: --output has to be specified if chunk is used!")
            return

        libname = "step_" + re.sub("[^0-9]", "", str(step)) + "_" + str(crit_nb) + "_"
        libnames = list_lib(libname)

        if libnames == []:
            print("File for step not found!")
            start = input("Start? y/[n]: ")
            if start.upper() != "Y":
                return 0
            tic = time.time()
            wg.weights_generator_recurs_chunk(step, int_possible_weights, crit_nb, int_multiplier, int_multiplier, chunk_size, chunk_id)
            libnames = list_lib(libname)
        else:
            print("Found file for step " + str(step) + ":", libnames)
            start = input("Start? y/[n]: ")
            if start.upper() != "Y":
                return 0
            tic = time.time()

        for i in range(len(libnames)):
            chunk_weights = pickle.load(open(os.path.join(LIB_DIR, libnames[i]), "rb" ))
            print("Length of chunk_weights " + str(i) + ":", len(chunk_weights))
            print(time.time()-tic)
            if promethee_flag:
                chunk_weights = zip(itertools.repeat(alt_eval), chunk_weights, itertools.repeat(func_pref_crit), itertools.repeat(alt_names))
                chunk_rankings = generate_all_rankings2(pool, chunk_weights, func_pref_crit, alt_names, alt_eval)
            elif maut_flag:
                chunk_weights = zip(itertools.repeat(alt_eval), itertools.repeat(alt_names), chunk_weights)
                chunk_rankings = generate_all_maut_rankings(pool, chunk_weights)
            chunk_filename = filename + "_" + str(i) + ".sav"
            if not statonly:
                pickle.dump([possible_weights, chunk_rankings], open(chunk_filename,'wb'),pickle.HIGHEST_PROTOCOL)
            else:
                pass
    else:
        if randomweights == 0:
            libname = os.path.join(LIB_DIR, "step_" + re.sub("[^0-9]", "", str(step)) + "_" + str(crit_nb) + ".sav")
            try:    
                all_weights = pickle.load(open(libname, "rb" ))
                print("Found file for step " + str(step) + ":", libname)
                start = input("Start? y/[n]: ")
                if start.upper() != "Y":
                    return 0
                # tic = time.time()
            except:
                print("File for step not found!")
                start = input("Start? y/[n]: ")
                if start.upper() != "Y":
                    return 0
                # tic = time.time()
                # wg.weights_generator(pool, chunk, step, possible_weights, crit_nb, int_multiplier, int_multiplier)
                wg.weights_generator_recurs_chunk(step, int_possible_weights, crit_nb, int_multiplier, int_multiplier, chunk_size, chunk_id)
                all_weights = pickle.load(open(libname, "rb" ))
        else:
            start = input("Start? y/[n]: ")
            if start.upper() != "Y":
                return 0
            all_weights = np.random.dirichlet(np.ones(crit_nb), size=randomweights)
            possible_weights = all_weights
        print("Length of all_weights:", len(all_weights))
        # print(time.time()-tic)
        if promethee_flag:
            all_weights = zip(itertools.repeat(alt_eval), all_weights, itertools.repeat(func_pref_crit), itertools.repeat(alt_names))
            all_rankings = generate_all_rankings2(pool, all_weights, func_pref_crit, alt_names, alt_eval)
        elif maut_flag:
            if not statonly:
                all_weights = zip(itertools.repeat(alt_eval), itertools.repeat(alt_names), all_weights)
                all_rankings = generate_all_maut_rankings(pool, all_weights)
            else:
                # all_weights = zip(itertools.repeat(distrib), itertools.repeat(alt_eval), itertools.repeat(alt_names), all_weights)
                distrib = generate_all_maut_distrib(pool, alt_eval, alt_names, all_weights)
        if args.output != None:
            if not statonly:
                pickle.dump([possible_weights, all_rankings], open(filename,'wb'),pickle.HIGHEST_PROTOCOL)
            else:
                pickle.dump([possible_weights, distrib], open(filename,'wb'),pickle.HIGHEST_PROTOCOL)

    # print(time.time()-tic)
    pool.close()
    pool.join()

if __name__ == "__main__":
    main()
