import pandas as pd
from lib import tsp
from lib import cs3ci

ulysses16_coords = pd.read_csv('ulysses16.csv',header=0).values
tsp_instance = tsp.construct_from_city_coords(ulysses16_coords)
TIME_LIMIT = 3

print('Running an EA for {} seconds'.format(
  TIME_LIMIT))

ea_route, ea_route_cost = cs3ci.ea.solve_tsp(
  tsp_instance,
  pop_size = 10,
  plot_fitness=True,
  time_limit = TIME_LIMIT
)

tsp.display_route(
  tsp_instance,ea_route, city_coords=ulysses16_coords,
  title="EA-generated route on the Ulysses16 TSP Instance.\n" +
    "Cost: {}".format(ea_route_cost)
)

# STEP 3: checks for both small and large population sizes

test_route, test_cost = cs3ci.ea.solve_tsp(
    tsp_instance,
    pop_size=test_pop_size,
    time_limit=TIME_LIMIT
)

print('pop_size={}: valid route = {}, cost = {}'.format(
    test_pop_size,
    tsp.is_valid_route(tsp_instance, test_route),
    test_cost
))


# STEP 7: comparing swap mutation with the novel EA, inversion mutation. 

N_RUNS = 10
COMPARE_POP_SIZE = 100
comparison_results = {}

for name, mutation in [('swap (baseline)', cs3ci.ea.swap_mutation),
                       ('inversion (novel)', cs3ci.ea.inversion_mutation)]:
  costs = []
  for run in range(N_RUNS):
    _, run_cost = cs3ci.ea.solve_tsp(
      tsp_instance,
      pop_size = COMPARE_POP_SIZE,
      mutation_operator = mutation,
      time_limit = TIME_LIMIT
    )
    costs.append(run_cost)
  comparison_results[name] = costs

  mean_cost = sum(costs) / len(costs)
  std_cost = (sum((c - mean_cost)**2 for c in costs) / (len(costs) - 1))**0.5
  print('{}: mean = {:.2f}, std = {:.2f}, best = {:.2f}, worst = {:.2f}'.format(
    name, mean_cost, std_cost, min(costs), max(costs)))
