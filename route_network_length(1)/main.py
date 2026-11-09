import pandas as pd
from lib import tsp

###############################################################################
# Step 1
###############################################################################

adjacency_matrix = [
  [0,20,42,35],
  [20,0,30,34],
  [42,30,0,12],
  [35,34,12,0]
]
small_tsp_instance = tsp.construct(adjacency_matrix)
tsp.display_instance(small_tsp_instance,label_edges=True,title="4-city TSP Instance")

# It would grow quadratically with the number of cities (AM is n x n)

###############################################################################
# Step 2
###############################################################################

test_route = [0,1,2,3,0]
test_route_cost = tsp.evaluate(small_tsp_instance,test_route)
tsp.display_route(small_tsp_instance,test_route,label_edges=True,
  title="Manually defined route on the 4-city TSP Instance\n" + 
  "Cost: {}".format(test_route_cost))

# Hand calculation: 0 to 1 (20) + 1 to 2 (30) + 2 to 3 (12) + 3 to 0 (35) = 97
print('Hand-calculated cost: 97, evaluate() says: {}'.format(test_route_cost))

###############################################################################
# Step 3
###############################################################################

random_route = tsp.random_route(small_tsp_instance)
random_route_cost = tsp.evaluate(small_tsp_instance, random_route)
tsp.display_route(small_tsp_instance,random_route,label_edges=True,
                    title="Random route on the 4-city TSP Instance.\n" + 
                      "Cost: {}".format(random_route_cost))

# Few random routes, viewing costs and min/max
random_costs = []
for _ in range(10):
  r = tsp.random_route(small_tsp_instance)
  random_costs.append(tsp.evaluate(small_tsp_instance, r))
print('Random route costs (4 cities): {}'.format(random_costs))
print('Min: {}, Max: {}'.format(min(random_costs), max(random_costs)))

###############################################################################
# Step 4
###############################################################################
ulysses16_coords = pd.read_csv('ulysses16.csv',header=0).values
ulysses16_tsp_instance = tsp.construct_from_city_coords(ulysses16_coords)

# As we have the (x,y) coordinates of the cities for the Ulysses16 problem, we
# can pass them to the display function to position the cities correctly when
# they are displayed.
ulysses16_route = tsp.random_route(ulysses16_tsp_instance)
ulysses16_route_cost = tsp.evaluate(ulysses16_tsp_instance, ulysses16_route)
tsp.display_route(
  ulysses16_tsp_instance,ulysses16_route,
  city_coords=ulysses16_coords,
  title="Random route on the Ulysses16 TSP Instance.\n" +
    "Cost: {}".format(ulysses16_route_cost)
)