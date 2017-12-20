#!/usr/bin/env python3

def weights_generator_recurs_fill(possible_weights, crit_nb, int_multiplier, all_weights, w_sum, result=[0], index=0):
    if index > crit_nb or w_sum < 0:
        return

    if index == crit_nb:
        if w_sum == 0:
            all_weights.append(result[:crit_nb])
            # yield result[:crit_nb]

        return

    for val in possible_weights:
        result[index] = val
        result.append(0)
        weights_generator_recurs_fill(possible_weights, crit_nb, int_multiplier, all_weights, w_sum-val, result, index + 1)

def weights_generator_iter(possible_weights, crit_nb, int_multiplier):
    pass

crit_nb = 4
possible_weights = [0, 50, 100]
int_multiplier = 100
chunk = True
all_weights = []
weights_generator_recurs_fill(possible_weights, crit_nb, int_multiplier, all_weights, int_multiplier)
# weights = list(weights)
# for val in weights:
#     print(val)
# print(len(weights))
