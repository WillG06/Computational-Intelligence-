from antennaarray import AntennaArray
import random
random.seed(42)

# A simple example of how the AntennaArray class could be used as part
# of a random search.

def random_parameters(antenna_array_problem):
    b = antenna_array_problem.bounds()  
    return [low + random.random()*(high-low) for [high, low] in b]

# Construct an instance of the antenna array problem with 3 antennae and a
# steering angle of 90 degree.
antenna_array_problem = AntennaArray(3, 90)

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









import statistics


# STEP 2: random search baseline
def random_valid_design(problem):

    """ n = number of antennae, d = minimum spacing, slack = remaining space to be distributed, u = random offsets"""

    n = problem.n_antennae                    
    aperture = n / 2
    d = AntennaArray.MIN_SPACING                                       #"""keep the minimum spacing between antennae"""
    slack = aperture - (n - 1) * d
    u = sorted(random.uniform(0, slack) for _ in range(n - 1))

    design = []
    for i in range(n - 1):
        design.append(u[i] + i * d)           # """Same use as is_Valid function"""
    design.append(aperture)

    return design


def random_search(problem, n_tries):
    
    """ n = number of antennae, d = minimum spacing, slack = remaining space to be distributed, u = random offsets"""

    best, best_cost = None, float('inf')
    for _ in range(n_tries):
        d = random_valid_design(problem)
        c = problem.evaluate(d)
        if c < best_cost:
            best, best_cost = d, c
    return best, best_cost


#STEP 3: particle swarm optimisation (PSO) 

class Particle:
    def __init__(self, problem):

        """declare the variables: problem, aperture, position, velocity, best position and best cost"""

        self.problem = problem
        self.aperture = problem.n_antennae / 2
        self.position = random_valid_design(problem)
       
        span = self.aperture
        self.velocity = [random.uniform(-span, span) * 0.1
                         for _ in range(problem.n_antennae - 1)]     + [0.0]  # """Last antenna pinned/ doesnt move"""

        self.best_position = list(self.position)
        self.best_cost = problem.evaluate(self.position)


    def update(self, global_best, w, c1, c2, vmax=None):


        """ 'invisible wall' constraint handler
        n = number of antennae, d = minimum spacing, slack = remaining space to be distributed, u = random offsets

        momentum = w * velocity, where w is the inertia weight
        cognitive = c1 * r1 * (pbest - position), 
        social = c2 * r2 * (gbest - position) 
        """
        
        """c1 and c2 are acceleration coefficients, 
        r1 and r2 are random numbers between 0 and 1, 
        w is the inertia weight, 
        and vmax is the maximum velocity allowed for each particle."""
        

        n = self.problem.n_antennae
        for i in range(n - 1):  # last antenna stays pinned 
            r1, r2 = random.random(), random.random()
            v = (w * self.velocity[i]
                 + c1 * r1 * (self.best_position[i] - self.position[i]) #pull to pbest
                 + c2 * r2 * (global_best[i] - self.position[i]))  #pull to gbest

            if vmax is not None:
                v = max(-vmax, min(vmax, v))
            self.velocity[i] = v                 # """if new best, save"""
            self.position[i] += v

        cost = self.problem.evaluate(self.position)  # inf if invalid
        if cost < self.best_cost:
            self.best_cost = cost
            self.best_position = list(self.position)


        return cost


#STEP 4: swarm of particles and PSO algorithm

class Swarm:
    def __init__(self, problem, size=20, w=(0.7298, 0.7298), c1=1.4962, c2=1.4962,
                 vmax_frac=None, restart_after=None):
        self.problem = problem
        self.particles = [Particle(problem) for _ in range(size)]
        self.w_start, self.w_end = w
        self.c1, self.c2 = c1, c2
        self.vmax = None if vmax_frac is None else vmax_frac * problem.n_antennae / 2
        self.restart_after = restart_after       # novel variant for particles that fail to improve for N iterations
        self.stagnant = [0] * size
        self.global_best = None
        self.global_best_cost = float('inf')
        self.evaluations = size                  # initial evaluations of particles
        self._update_global_best()

    def _update_global_best(self):
        for p in self.particles:
            if p.best_cost < self.global_best_cost:
                self.global_best_cost = p.best_cost
                self.global_best = list(p.best_position)

    def iterate(self, w):
        self._update_global_best()
        for k, p in enumerate(self.particles):     # """k is the index of the particle in the swarm, p is the particle object from swarm"""
            before = p.best_cost
            p.update(self.global_best, w, self.c1, self.c2, self.vmax)
            self.evaluations += 1

            if self.restart_after is not None:
                self.stagnant[k] = 0 if p.best_cost < before else self.stagnant[k] + 1
                if self.stagnant[k] >= self.restart_after and p.best_position != self.global_best:
          
                    fresh = Particle(self.problem)
                    self.evaluations += 1
                    self.particles[k] = fresh        #replace the stagnant particle with a new random one
                    self.stagnant[k] = 0

        self._update_global_best()

    def run(self, iterations, verbose=False):
        for t in range(iterations):
            frac = t / max(1, iterations - 1)
            w = self.w_start + (self.w_end - self.w_start) * frac
            self.iterate(w)
            if verbose:
                print("iter {:4d}  best SLL {:.4f}".format(t + 1, self.global_best_cost))
        return self.global_best, self.global_best_cost


#STEP 5: run standard and novel PSO variants

def run_standard_pso(problem, iterations, size=20):
    # Constriction-style constants (Clerc & Kennedy): w=0.7298, c1=c2=1.4962
    return Swarm(problem, size).run(iterations)


def run_novel_pso(problem, iterations, size=20):
    # Novel variant: inertia weight decreases from 0.9 to 0.4, c1= c2= 2.0, 
    # inertia is how much 'problem' is retained from last iteration
    return Swarm(problem, size, w=(0.9, 0.4), c1=2.0, c2=2.0,
                 vmax_frac=0.2, restart_after=8).run(iterations)


def compare(n_antennae, steering, runs, iterations, size=20):
    problem = AntennaArray(n_antennae, steering)
    budget = size * (iterations + 1)
    results = {"random": [], "standard": [], "novel": []}

    for r in range(runs):
        random.seed(1000 + r)
        results["random"].append(random_search(problem, budget)[1])
        random.seed(1000 + r)
        results["standard"].append(run_standard_pso(problem, iterations, size)[1])
        random.seed(1000 + r)
        results["novel"].append(run_novel_pso(problem, iterations, size)[1])
    print("\n{} antennae, steering {}, ~{} evaluations/run, {} runs".format(
        n_antennae, steering, budget, runs))

    for name, vals in results.items():
        print("  {:9s} mean {:7.3f}  sd {:6.3f}  best {:7.3f}  worst {:7.3f}".format(
            name, statistics.mean(vals), statistics.pstdev(vals), min(vals), max(vals)))
    

    try:
        from scipy.stats import mannwhitneyu
        for a, b in [("standard", "random"), ("novel", "random"), ("novel", "standard")]:
            p = mannwhitneyu(results[a], results[b], alternative="two-sided").pvalue
            print("  Mann-Whitney {} vs {}: p = {:.4f}".format(a, b, p))
    except ImportError:
        print("  (install scipy for significance tests: pip install scipy)")
    return results


if __name__ == "__main__":
    # Step 1: looking for 5.49 dB 3 antenna
    p3 = AntennaArray(3, 90)
    print("Regular spacing peak SLL (expect ~5.49):", round(p3.evaluate([0.5, 1.0, 1.5]), 2))

    # Step 2: 
    random.seed(1)
    print("Random search, 3 antennae, 500 tries:", random_search(AntennaArray(3, 90), 500)[1])
    print(best_parameters)
    print(antenna_array_problem.is_valid(best_parameters))

    # Step 5: 
    random.seed(1)
    print("\nStandard PSO progress (3 antennae):")
    Swarm(AntennaArray(3, 90)).run(30, verbose=True)

    #step 5/6:
    RUNS, ITERS = 10, 50
    compare(3, 90, RUNS, ITERS)
    compare(10, 90, RUNS, ITERS)