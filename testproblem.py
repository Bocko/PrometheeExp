from prefFunc import *
import csv_file

def subset_bestcities():
    criteria_names = ['Stability', 'Healthcare', 'Culture and Environment', 'Education', 'Infrastructure', 'Spatial Characteristics'] 

    original_weights = [0.1875, 0.15, 0.1875, 0.075, 0.15, 0.25]

    func_pref_crit = [PreferenceType2(0), PreferenceType2(0), PreferenceType2(0),  PreferenceType2(0), PreferenceType2(0), PreferenceType2(0)]

    alt_names = ['Hanoi', 'Lagos', 'Chicago', 'Stockholm', 'London', 'Santiago', 'Munich', 'Tehran', 'Rome', 'Boston', 'New York', 'Tokyo', 'Casablanca', 'Kiev', 'Abidjan']

    alt_eval = [[55, 54.2, 53.7, 58.3, 51.8, 38.4], [25, 33.3, 52.3, 33.3, 48.2, 22.3], [85, 91.7, 91.7, 100, 92.9, 52.7], [95, 95.8, 91.2, 100, 96.4, 58.9], [70, 87.5, 97.2, 100, 89.3, 72.6], [75, 70.8, 89.1, 83.3, 85.7, 35.1], [85, 100, 97.2, 91.7, 89.3, 62.5], [50, 62.5, 35.9, 50, 33.9, 53.6], [80, 87.5, 91.7, 100, 92.9, 67.3], [80, 91.7, 91.7, 100, 96.4, 46.7], [70, 91.7, 91.7, 100, 89.3, 65.2], [90, 100, 94.4, 100, 92.9, 53.3], [65, 45.8, 60.9, 58.3, 60.7, 43.8], [70, 75, 73.4, 83.3, 50, 33.3], [25, 45.8, 54.2, 50, 53.6, 30.1]]


    return criteria_names, original_weights, func_pref_crit, alt_names, alt_eval

def epi2016():
    original_weights, criteria_names, alt_names, alt_eval = csv_file.open_csv('epi2016/epi-2016.csv')
    func_pref_crit = [PreferenceType2(0) for i in range(len(criteria_names))]
    return criteria_names, original_weights, func_pref_crit, alt_names, alt_eval

def hdi2016():
    original_weights, criteria_names, alt_names, alt_eval = csv_file.open_csv('hdi/hdi2016.csv')
    func_pref_crit = [PreferenceType2(0) for i in range(len(criteria_names))]
    return criteria_names, original_weights, func_pref_crit, alt_names, alt_eval

def studentcities2017():
    original_weights, criteria_names, alt_names, alt_eval = csv_file.open_csv('studentcities/studentcities2017.csv')
    func_pref_crit = [PreferenceType2(0) for i in range(len(criteria_names))]
    return criteria_names, original_weights, func_pref_crit, alt_names, alt_eval

def safecities2017():
    original_weights, criteria_names, alt_names, alt_eval = csv_file.open_csv('safecities/eiu_safecities2017.csv')
    func_pref_crit = [PreferenceType2(0) for i in range(len(criteria_names))]
    return criteria_names, original_weights, func_pref_crit, alt_names, alt_eval

def foodsecurity2017():
    original_weights, criteria_names, alt_names, alt_eval = csv_file.open_csv('gfsi/gfsi2017.csv')
    func_pref_crit = [PreferenceType2(0) for i in range(len(criteria_names))]
    return criteria_names, original_weights, func_pref_crit, alt_names, alt_eval

def democracy2017():
    original_weights, criteria_names, alt_names, alt_eval = csv_file.open_csv('democracy/di2017.csv')
    func_pref_crit = [PreferenceType2(0) for i in range(len(criteria_names))]
    return criteria_names, original_weights, func_pref_crit, alt_names, alt_eval