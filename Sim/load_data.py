#!/usr/bin/env python3

import argparse
import pickle
import copy

def parse_args():
    parser = argparse.ArgumentParser(description = 'Promethee Expressivity')
    parser.add_argument("filename", nargs=1, type=str)
    parser.add_argument('-c', '--compare', nargs=1, type=str)
    args = parser.parse_args()
 
    return args

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

def print_fileinfo(filename, possible_weights, unique_rankings):
    print("File", filename)
    print("Possible weights:", possible_weights)
    print("Unique rankings:", unique_rankings)
    print("Length:", len(unique_rankings))
    print("---")

def load_data():
    args = parse_args()
    filename = args.filename[0]
    [possible_weights, unique_rankings] = pickle.load(open(filename, "rb" ))
    print_fileinfo(filename, possible_weights, unique_rankings)

    if args.compare != None:
        filename2 = args.compare[0]
        [possible_weights2, unique_rankings2] = pickle.load(open(filename2, "rb" ))
        print_fileinfo(filename2, possible_weights2, unique_rankings2)
        common, different1, different2 = compare(possible_weights, unique_rankings, possible_weights2, unique_rankings2)
        print("Common:", common)
        print("Unique in first file:", different1)
        print("Unique in second file:", different2)

if __name__ == "__main__":
    load_data()