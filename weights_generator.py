#!/usr/bin/env python3

import argparse
import numpy as np
import itertools
import csv_file
import multiprocessing
import time
import re
import pickle

LIB_DIR = 'lib'

def parse_args():
    parser = argparse.ArgumentParser(description = 'Promethee Expressivity')

    parser.add_argument('-s','--step', nargs=1, type=float, required=True)
    parser.add_argument('-n', '--crit_nb', nargs=1, type=int, required=True)
    parser.add_argument('-m', '--multiplier', nargs=1, type=int)
    parser.add_argument('-c', '--chunk_size', nargs=1, type=int)

    parser.add_argument('-o','--output', nargs=1)

    args = parser.parse_args()
    return args

def weights_choice(step):
    start = 0
    stop = 1
    np_step = int(1 / step + 1)

    return np.linspace(start,stop,np_step)

def weights_generator_recurs(possible_weights, crit_nb, int_multiplier, w_sum, result, index):
    if index > crit_nb or w_sum < 0:
        return

    if index == crit_nb:
        if w_sum == 0:
            # print(result[:n])
            yield np.array(result[:crit_nb]) / int_multiplier
            # yield np.array(result[:crit_nb]) / int_multiplier

        return

    for val in possible_weights:
        result[index] = val
        result.append(0)
        yield from weights_generator_recurs(possible_weights, crit_nb, int_multiplier, w_sum-val, result, index + 1)

def weights_generator_func(par_weights):
    (val, possible_weights, crit_nb, int_multiplier, w_sum) = par_weights
    result = [val]
    result.append(0)
    yield from weights_generator_recurs(possible_weights, crit_nb, int_multiplier, w_sum-val, result, 1)

def weights_generator(pool, chunk, step, possible_weights, crit_nb, int_multiplier, w_sum):
    # par_weights = [(val, alt_eval, int_possible_weights, func_pref_crit, alt_names, int_multiplier, w_sum) for val in int_possible_weights]
    par_weights = [(val, possible_weights, crit_nb, int_multiplier, w_sum) for val in possible_weights]
    all_weights = []
    for i in range(len(par_weights)):
        weights = weights_generator_func(par_weights[i])
        weights = list(weights)
        if chunk:
            libname = "lib/step_" + re.sub("[^0-9]", "", str(step)) + "_" + str(crit_nb) + "_" + str(i) + ".sav"
            pickle.dump(weights, open(libname,'wb'),pickle.HIGHEST_PROTOCOL)
        else:
            all_weights.extend(weights)
    
    if not chunk:
        all_weights = list(all_weights)
        libname = "lib/step_" + re.sub("[^0-9]", "", str(step)) + "_" + str(crit_nb) + ".sav"
        pickle.dump(all_weights, open(libname,'wb'),pickle.HIGHEST_PROTOCOL)

def weights_generator_recurs_fill(step, possible_weights, crit_nb, int_multiplier, weights_list, w_sum, chunk_size, chunk_id, result=[0], index=0):
    if index > crit_nb or w_sum < 0:
        return

    if index == crit_nb:
        if w_sum == 0:
            weights_list.append(np.array(result[:crit_nb]) / int_multiplier)
            if chunk_size != 0 and len(weights_list) == chunk_size:
                libname = "lib/step_" + re.sub("[^0-9]", "", str(step)) + "_" + str(crit_nb) + "_" + str(chunk_id[0]) + ".sav"
                pickle.dump(weights_list, open(libname,'wb'),pickle.HIGHEST_PROTOCOL)
                del weights_list[:]
                chunk_id[0] += 1

        return

    for val in possible_weights:
        result[index] = val
        result.append(0)
        weights_generator_recurs_fill(step, possible_weights, crit_nb, int_multiplier, weights_list, w_sum-val, chunk_size, chunk_id, result, index + 1)

def weights_generator_recurs_chunk(step, possible_weights, crit_nb, int_multiplier, w_sum, chunk_size, chunk_id, result=[0], index=0):
    weights_list = []
    weights_generator_recurs_fill(step, possible_weights, crit_nb, int_multiplier, weights_list, int_multiplier, chunk_size, chunk_id)
    if len(weights_list) != 0:
        if chunk_size != 0:
            libname = "lib/step_" + re.sub("[^0-9]", "", str(step)) + "_" + str(crit_nb) + "_" + str(chunk_id[0]) + ".sav"
            pickle.dump(weights_list, open(libname,'wb'),pickle.HIGHEST_PROTOCOL)
        else:
            libname = "lib/step_" + re.sub("[^0-9]", "", str(step)) + "_" + str(crit_nb) + ".sav"
            pickle.dump(weights_list, open(libname,'wb'),pickle.HIGHEST_PROTOCOL)

def main():
    # pool = multiprocessing.Pool(4)

    args = parse_args()
    if args.step[0] > 0:
        step = args.step[0]
    else:
        raise('Please enter positive step value')

    print("Generation data:")
    
    possible_weights = weights_choice(step)
    print("Possible weights:", possible_weights)

    if args.chunk_size != None:
        chunk_size = args.chunk_size[0]
    else:
        chunk_size = 0
    chunk_id = [0]

    print("Chunk size:", chunk_size)

    crit_nb = args.crit_nb[0]

    if args.multiplier != None:
        int_multiplier = args.multiplier[0]
    else:
        int_multiplier = 100

    start = input("Start? y/[n]: ")
    if start.upper() != "Y":
        return 0

    int_possible_weights = (possible_weights * int_multiplier).astype(int)
    weights_generator_recurs_chunk(step, int_possible_weights, crit_nb, int_multiplier, int_multiplier, chunk_size, chunk_id)
    # weights_generator(pool, chunk, step, int_possible_weights, crit_nb, int_multiplier, int_multiplier)


    # pool.close()
    # pool.join()

if __name__ == "__main__":
    main()
