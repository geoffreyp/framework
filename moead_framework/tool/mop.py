import random
import numpy as np


def is_pareto_efficient(costs, return_mask = True):
    """
    Find the pareto-efficient points

    :param costs: An (n_points, n_costs) array
    :param return_mask: True to return a mask
    :return: An array of indices of pareto-efficient points.
        If return_mask is True, this will be an (n_points, ) boolean array
        Otherwise it will be a (n_efficient_points, ) integer array of indices.
    """
    is_efficient = np.arange(costs.shape[0])
    n_points = costs.shape[0]
    next_point_index = 0  # Next index in the is_efficient array to search for
    while next_point_index < len(costs):
        nondominated_point_mask = np.any(costs < costs[next_point_index], axis=1)
        nondominated_point_mask[next_point_index] = True
        is_efficient = is_efficient[nondominated_point_mask]  # Remove dominated points
        costs = costs[nondominated_point_mask]
        next_point_index = np.sum(nondominated_point_mask[:next_point_index])+1
    if return_mask:
        is_efficient_mask = np.zeros(n_points, dtype=bool)
        is_efficient_mask[is_efficient] = True
        return is_efficient_mask
    else:
        return is_efficient


def get_non_dominated(population):
    """
    Return all non dominated solutions of the population

    :param population: list<{:class:`~moead_framework.solution.one_dimension_solution.OneDimensionSolution`}>
    :return: population: list<{:class:`~moead_framework.solution.one_dimension_solution.OneDimensionSolution`}>
    """
    arr = []
    for s in population:
        arr.append(s.F)

    new_pop = list(population[i] for i in is_pareto_efficient(np.array(arr), return_mask=False))

    return new_pop


def is_duplicated(x, population, number_of_objective):
    """
    Identify if the solution x is already in the population

    :param number_of_objective: integer
    :param x: {:class:`~moead_framework.solution.one_dimension_solution.OneDimensionSolution`}
    :param population: list<{:class:`~moead_framework.solution.one_dimension_solution.OneDimensionSolution`}>
    :return: boolean
    """
    for sol in population:
        is_dup = True
        for i in range(number_of_objective):
            if sol.F[i] != x.F[i]:
                is_dup = False
                break

        if is_dup:
            return True

    return False


def population_size_without_duplicate(population):
    """
    Compute the population size without duplicate

    :param population: list<{:class:`~moead_framework.solution.one_dimension_solution.OneDimensionSolution`}>
    :return: integer: the size of the population
    """
    arr = []
    for ind in population:
        is_dup = False
        for ind_not_dup in arr:
            if np.array_equal(np.array(ind.decision_vector), np.array(ind_not_dup.decision_vector)):
                is_dup = True

        if not is_dup:
            arr.append(ind)

    return len(arr)


def compute_crowding_distance(s):
    """
    Update the attribute distance of each solution with the crowding distance

    :param s: list<{:class:`~moead_framework.solution.one_dimension_solution.OneDimensionSolution`}>
    :return: population: list<{:class:`~moead_framework.solution.one_dimension_solution.OneDimensionSolution`}> with computed distances
    """
    for individual in s:
        individual.distance = 0

    max_distance = 0
    for m in range(len(s[0].F)):
        s.sort(key=lambda x: x[m])

        for i in range(1, len(s) - 1):
            s[i].distance = s[i].distance + (s[i + 1][m] - s[i - 1][m])
            max_distance = max(max_distance, s[i].distance)

    s[0].distance = max_distance
    s[len(s) - 1].distance = max_distance

    return s


def generate_weight_vectors(weight_file, shuffle=True):
    file = open(weight_file, 'r')
    file_content = list(map(str.strip, file.readlines()))
    weights = []
    for row in file_content:
        weights.append(np.array(row.split(" ")).astype(np.float))

    if shuffle:
        random.shuffle(weights)

    file.close()
    return weights
