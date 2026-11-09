import time
import random
import math
import copy
import pandas as pd

#run foundations
coords = pd.read_csv("ulysses16.csv").values  
n = len(coords)
dist = [[math.dist(coords[i], coords[j]) for j in range(n)] for i in range(n)]

def evaluate_tsp(dist, route):
    return sum(dist[route[i]][route[i + 1]] for i in range(len(route) - 1))

def random_route(n):
    middle = list(range(1, n))
    random.shuffle(middle)
    return [0] + middle + [0]

#random search function
def random_search(dist, time_limit):
    n = len(dist)
    start = time.time()
    best_route = random_route(n)
    best_cost = evaluate_tsp(dist, best_route)
    while time.time() - start < time_limit:
        route = random_route(n)
        cost = evaluate_tsp(dist, route)
        if cost < best_cost:
            best_route, best_cost = route, cost
    return best_route, best_cost

#this is the city swap neighbourhood function, which generates all possible routes by swapping two cities in the current route
def city_swap_neighbourhood(route):
    neighbours = []
    for i in range(1, len(route) - 1):          # skip fixed 0 at both ends
        for j in range(i + 1, len(route) - 1):
            new_route = copy.deepcopy(route)
            new_route[i], new_route[j] = new_route[j], new_route[i]
            neighbours.append(new_route)
    return neighbours


def best_neighbour(dist, neighbourhood):
    return min(neighbourhood, key=lambda r: evaluate_tsp(dist, r))

#local search == finds local optimum
def local_search(dist, time_limit):
    n = len(dist)
    start = time.time()
    best_route, best_cost = None, float("inf")

    while time.time() - start < time_limit:
        current = random_route(n)
        current_cost = evaluate_tsp(dist, current)

        while time.time() - start < time_limit:
            candidate = best_neighbour(dist, city_swap_neighbourhood(current))
            candidate_cost = evaluate_tsp(dist, candidate)
            if candidate_cost < current_cost:
                current, current_cost = candidate, candidate_cost
            else:
                break  # local optimum reached, go again

        if current_cost < best_cost:
            best_route, best_cost = current, current_cost

    return best_route, best_cost


def two_opt_neighbourhood(route):
    neighbours = []
    for i in range(1, len(route) - 2):
        for j in range(i + 1, len(route) - 1):
            new_route = copy.deepcopy(route)
            new_route[i:j + 1] = new_route[i:j + 1][::-1]
            neighbours.append(new_route)
    return neighbours

# ---------- Tests ----------
if __name__ == "__main__":
    print(city_swap_neighbourhood([0, 1, 2, 3, 4, 0]))  # should match the lab sheet
    for t in [1, 5, 30]:
        print("random", t, random_search(dist, t)[1])
        print("local ", t, local_search(dist, t)[1])