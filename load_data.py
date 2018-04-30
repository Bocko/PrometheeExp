#!/usr/bin/env python3

import argparse
import pickle
import copy
import numpy as np
import matplotlib.pyplot as plt

def parse_args():
    parser = argparse.ArgumentParser(description = 'Promethee Expressivity')
    parser.add_argument("filename", nargs=1, type=str)
    parser.add_argument('-t','--stability', nargs=1, type=int)
    parser.add_argument('-c', '--compare', nargs=1, type=str)
    parser.add_argument('-p', '--plot', nargs=2, type=str)
    args = parser.parse_args()
 
    return args

def filter_unique_rankings(all_rankings, stability_level):
    unique_rankings = []
    for ranking, netflows in all_rankings:
        # if stability_level != 0:
            if ranking[:stability_level] not in unique_rankings:
                unique_rankings.append(ranking[:stability_level])
                # print(ranking[:stability_level])

        # else:
        #     if ranking not in unique_rankings:
        #         unique_rankings.append(ranking)

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

def plot_data(all_rankings, stability_level, plot_filename, plot_type):
    if plot_type == "distribution":
        plot_distribution(all_rankings, stability_level, plot_filename, plot_type)

def plot_distribution(all_rankings, stability_level, plot_filename, plot_type):
    distrib = compute_distribution(all_rankings, stability_level)
    distrib_rankings = sorted(distrib, key=distrib.get)
    distrib_values = sorted(distrib.values())
    total_obs = sum(distrib_values)
    median_val = distrib_values[-1]
    median_idx = len(distrib_rankings) - 1
    while median_val < total_obs // 2 and median_idx >= 0:
        median_idx -= 1
        median_val += distrib_values[median_idx]
    median_prop = (len(distrib_values) - median_idx) / len(distrib_values)
    print("{:.2%}".format(median_prop))

    y = np.arange(len(distrib_rankings))
    plt.barh(y, distrib_values)
    plt.plot([-5, max(distrib_values)], [median_idx-0.5, median_idx-0.5], "r--")
    plt.xlabel("Occurrences (total: " + str(total_obs) + " observations)")
    if stability_level <= 3:
        plt.yticks(y, distrib_rankings, fontsize=10)
    else:
        plt.yticks([], [])
    plt.text(max(distrib_values)*0.9, median_idx-0.4, "median (" + "{:.2%}".format(median_prop) + ")", {"color": 'r', "fontsize": 10})
    # plt.get_current_fig_manager().window.showMaximized()
    # plt.tight_layout()
    plt.show()

def plot_compare(all_rankings, all_rankings2, stability_level, plot_filename, plot_type):
    unique_rankings = filter_unique_rankings(all_rankings, stability_level)
    unique_rankings2 = filter_unique_rankings(all_rankings2, stability_level)
    common, different1, different2 = compare(possible_weights, unique_rankings, possible_weights2, unique_rankings2)
    distrib = compute_distribution(all_rankings, stability_level)
    distrib_rankings = sorted(distrib, key=distrib.get)
    distrib_values = sorted(distrib.values())
    total_obs = sum(distrib_values)
    median_val = distrib_values[-1]
    median_idx = len(distrib_rankings) - 1
    while median_val < total_obs // 2 and median_idx >= 0:
        median_idx -= 1
        median_val += distrib_values[median_idx]
    median_prop = (len(distrib_values) - median_idx) / len(distrib_values)
    print("{:.2%}".format(median_prop))

    fig, ax = plt.subplots()
    y = np.arange(len(distrib_rankings))
    barlist = plt.barh(y, distrib_values)
    plt.xlabel("Occurrences (total: " + str(total_obs) + " observations)")

    plt.yticks(y, distrib_rankings, fontsize=10)

    colors_tick= ['k' for i in range(len(distrib_rankings))]
    colors_bar = ['xkcd:cerulean' for i in range(len(distrib_rankings))]
    for r in different1:
        colors_tick[distrib_rankings.index(tuple(r))] = 'r'
        colors_bar[distrib_rankings.index(tuple(r))] = 'r'

    for bar, ytick, ct, cb in zip(barlist, ax.get_yticklabels(), colors_tick, colors_bar):
        ytick.set_color(ct)
        bar.set_color(cb)

    if stability_level > 3:
        plt.yticks([], [])

    plt.plot([0, max(distrib_values)], [median_idx-0.5, median_idx-0.5], "g--")
    plt.text(max(distrib_values)*0.9, median_idx-0.4, "median (" + "{:.2%}".format(median_prop) + ")", {"color": 'g', "fontsize": 10})
    plt.show()

def compute_distribution(all_rankings, stability_level):
    distrib = {}
    for ranking, netflows in all_rankings:
        tranking = tuple(ranking)
        # if stability_level != 0:
            distrib[tranking[:stability_level]] = distrib.get(tranking[:stability_level],0) + 1
        # else:
        #     distrib[tranking] = distrib.get(tranking,0) + 1

    return distrib


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
        if args.stability[0] == 0:
            raise ValueError("Stability level cannot be 0")
        else:
        stability_level = args.stability[0]
    else:
        stability_level = 1

    [possible_weights, all_rankings] = pickle.load(open(filename, "rb" ))
    unique_rankings = filter_unique_rankings(all_rankings, stability_level)
    print_fileinfo(filename, stability_level, possible_weights, unique_rankings)

    if args.compare != None:
        filename2 = args.compare[0]
        [possible_weights2, all_rankings2] = pickle.load(open(filename2, "rb" ))
        unique_rankings2 = filter_unique_rankings(all_rankings2, stability_level=stability_level)
        print_fileinfo(filename2, stability_level, possible_weights2, unique_rankings2)
        common, different1, different2 = compare(possible_weights, unique_rankings, possible_weights2, unique_rankings2)
        print("Common:", common)
        print("Length common:", len(common))
        print("Unique in first file:", different1)
        print("Length unique first:", len(different1))
        print("Unique in second file:", different2)
        print("Length unique second:", len(different2))

    if args.plot != None:
        plot_filename = args.plot[0]
        plot_type = args.plot[1]
        plot_data(all_rankings, stability_level, plot_filename, plot_type)

if __name__ == "__main__":
    load_data()

    # filename = "epi2016/epi2016_01.sav"
    # stability_level = 1
    # [possible_weights, all_rankings] = pickle.load(open(filename, "rb" ))
    # distrib = compute_distribution(all_rankings, stability_level)