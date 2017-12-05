import csv
def open_csv(filename):
    epi = []
    with open(filename, newline='') as csvfile:
        content = csv.reader(csvfile, delimiter=';', quotechar='|')
        for row in content:
            epi.append(row)

    weights = list(map(lambda x: float(x), epi[0][3:]))
    criteria = epi[1][3:]
    all_names = []
    all_alternatives = []
    for row in epi[2:]:
        all_names.append(row[2])
        all_alternatives.append(list(map(lambda x: float(x), row[3:])))

    return weights, criteria, all_names, all_alternatives
