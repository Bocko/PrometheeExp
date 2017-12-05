#!/usr/bin/env python3

import argparse
import pickle

def parse_args():
    parser = argparse.ArgumentParser(description = 'Promethee Expressivity')
    parser.add_argument("filename", nargs=1, type=str)
    args = parser.parse_args()
 
    return args

def load_data():
    args = parse_args()
    filename = args.filename[0]
    [possible_weights, unique_rankings] = pickle.load(open(filename, "rb" ))
    print("Possible weights:", possible_weights)
    print("Unique rankings:", unique_rankings)
    print("Length:", len(unique_rankings))

if __name__ == "__main__":
    load_data()