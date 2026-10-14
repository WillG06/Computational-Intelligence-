from antennaarray import AntennaArray
import random
random.seed(42)

# A simple example of how the AntennaArray class could be used as part
# of a random search.

def random_parameters(antenna_array_problem):
    b = antenna_array_problem.bounds()  
    return [low + random.random()*(high-low) for [high, low] in b]

# Construct an instance of the antenna array problem with 3 antennae and a
# steering angle of 45 degree.
antenna_array_problem = AntennaArray(3,45)

###############################################################################
# NOTE: This attempt at solving the problem will work really badly! We        #
# haven't taken constraints into account when generating random parameters.   #
# The probability of randomly generating a design which meets the aperture    #
# size constraint is close to zero. This is just intended as an illustration. #
###############################################################################

# Generate N_TRIES random parameters and measure their peak SLL on the problem,
# saving the best parameters.
N_TRIES = 100
best_parameters = random_parameters(antenna_array_problem)
best_sll = antenna_array_problem.evaluate(best_parameters)
for _ in range(N_TRIES - 1):
    parameters = random_parameters(antenna_array_problem)
    # Note: in this example we are not testing parameters for validity. The
    # evaluate function penalises invalid solutions by assigning them the
    # maximum possible floating point value.
    sll = antenna_array_problem.evaluate(parameters)
    if sll < best_sll:
        best_sll = sll
        best_parameters = parameters

print("Best peak SLL after {} iterations based on random initialisation: {}".format(
  N_TRIES, best_sll))
  
###############################################################################
# How can we improve on the above attempt? By trying to generate initial      #
# parameters which meet the aperture size constraint!                         #
###############################################################################

def constrained_random_parameters(antenna_array_problem):
    b = antenna_array_problem.bounds()  
    design = [low + random.random()*(high-low) for [high, low] in b]
    design[-1] = antenna_array_problem.n_antennae/2
    return design
    
# Try random search again with this new method of generating parameters.
N_TRIES = 1000
best_parameters = constrained_random_parameters(antenna_array_problem)
best_sll = antenna_array_problem.evaluate(best_parameters)
for _ in range(N_TRIES - 1):
    parameters = constrained_random_parameters(antenna_array_problem)
    sll = antenna_array_problem.evaluate(parameters)
    if sll < best_sll:
        best_sll = sll
        best_parameters = parameters

print("Best peak SLL after {} iterations based on random initialisation: {}".format(
  N_TRIES, best_sll))