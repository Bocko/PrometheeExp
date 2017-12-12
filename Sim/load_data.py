#!/usr/bin/env python3

import argparse
import pickle
import copy

def parse_args():
    parser = argparse.ArgumentParser(description = 'Promethee Expressivity')
    parser.add_argument("filename", nargs=1, type=str)
    parser.add_argument('-t','--stability', nargs=1, type=int)
    parser.add_argument('-c', '--compare', nargs=1, type=str)
    args = parser.parse_args()
 
    return args

def filter_unique_rankings(all_rankings, stability_level=0):
    unique_rankings = []
    for ranking, netflows in all_rankings:
        if stability_level != 0:
            if ranking[:stability_level] not in unique_rankings:
                unique_rankings.append(ranking[:stability_level])
                # print(ranking[:stability_level])

        else:
            if ranking not in unique_rankings:
                unique_rankings.append(ranking)

    return unique_rankings

def compare(possible_weights1, unique_rankings1, possible_weights2, unique_rankings2):
    if len(unique_rankings1[0]) != len(unique_rankings2[0]):
        raise("Different stability levels")
    else:
        common = []
        different1 = []
        different2 = copy.deepcopy(unique_rankings2)
        for elem in unique_rankings1:
            if elem in unique_rankings2:
                common.append(elem)
                different2.remove(elem)
            else:
                different1.append(elem)

    return common, different1, different2

def print_fileinfo(filename, stability_level, possible_weights, unique_rankings):
    print("File", filename)
    print("Stability level:", stability_level)
    print("Possible weights:", possible_weights)
    print("Unique rankings:", unique_rankings)
    print("Length:", len(unique_rankings))
    print("---")

def load_data():
    args = parse_args()
    filename = args.filename[0]
    if args.stability != None:
        stability_level = args.stability[0]
    else:
        stability_level = 1
    [possible_weights, all_rankings] = pickle.load(open(filename, "rb" ))
    unique_rankings = filter_unique_rankings(all_rankings, stability_level=stability_level)
    print_fileinfo(filename, stability_level, possible_weights, unique_rankings)

    if args.compare != None:
        filename2 = args.compare[0]
        [possible_weights2, all_rankings2] = pickle.load(open(filename2, "rb" ))
        unique_rankings = filter_unique_rankings(all_rankings2, stability_level=stability_level)
        print_fileinfo(filename2, possible_weights2, unique_rankings2)
        common, different1, different2 = compare(possible_weights, unique_rankings, possible_weights2, unique_rankings2)
        print("Common:", common)
        print("Length:", len(common))
        print("Unique in first file:", different1)
        print("Length:", len(different1))
        print("Unique in second file:", different2)
        print("Length:", len(different2))

if __name__ == "__main__":
    load_data()