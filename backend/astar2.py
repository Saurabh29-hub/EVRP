import numpy as np
import random
from deap import base, creator, tools, algorithms

def run_evrp_ga(data):
    # ==== Step 1: Extract Data and Prepare Distance Matrix ====
    def extract_data(data):
        node_priority = {'depot': 0, 'customer': 1, 'station': 2}
        sorted_nodes = sorted(data['nodes'], key=lambda n: node_priority[n['type']])
        node_id_to_index = {node['id']: idx for idx, node in enumerate(sorted_nodes)}
        n = len(sorted_nodes)
        distance_matrix = np.full((n, n), np.inf)
        np.fill_diagonal(distance_matrix, 0)

        for edge in data['edges']:
            src = node_id_to_index[edge['source']]
            tgt = node_id_to_index[edge['target']]
            dist = edge['distance']
            distance_matrix[src][tgt] = dist
            distance_matrix[tgt][src] = dist
        print("distance_matrix: ")
        print(distance_matrix)
        return distance_matrix, sorted_nodes, node_id_to_index

    distance_matrix, sorted_nodes, node_id_to_index = extract_data(data)

    # ==== Step 2: Set Problem Parameters ====
    depot = 0
    charging_stations = [i for i, n in enumerate(sorted_nodes) if n['type'] == 'station']
    customer_nodes = [i for i, n in enumerate(sorted_nodes) if n['type'] == 'customer']
    num_customers = len(customer_nodes)
    max_capacity = data['vehicles'][0]['battery_capacity']
    energy_consumption_rate = data['constraints']['energy_consumption_rate']
    min_battery_threshold = data['constraints']['min_battery_threshold'] * max_capacity
    num_generations = 100
    population_size = 50
    mutation_prob = 0.2
    crossover_prob = 0.7

    # ==== Step 3: DEAP Setup ====
    if not hasattr(creator, "FitnessMin"):
        creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
    if not hasattr(creator, "Individual"):
        creator.create("Individual", list, fitness=creator.FitnessMin)

    toolbox = base.Toolbox()

    # Use closure to bind variables into evaluate()
    def make_evaluate(distance_matrix, sorted_nodes, depot, charging_stations, customer_nodes,
                      max_capacity, energy_consumption_rate, min_battery_threshold):
        def evaluate(individual):
            total_distance = 0
            total_energy = max_capacity
            prev_node = depot
            visited_customers = set()

            for node in individual:
                dist = distance_matrix[prev_node][node]
                if dist == np.inf:
                    return 9999.0,

                total_distance += dist
                total_energy -= dist * energy_consumption_rate

                if sorted_nodes[node]['type'] == 'customer':
                    visited_customers.add(node)

                if total_energy < min_battery_threshold:
                    if node in charging_stations:
                        total_energy = max_capacity
                    else:
                        return 9999.0,  # Out of energy

                prev_node = node

            if distance_matrix[prev_node][depot] == np.inf:
                return 9999.0,
            total_distance += distance_matrix[prev_node][depot]

            if set(customer_nodes) - visited_customers:
                return 9999.0,

            return total_distance,
        return evaluate

    evaluate_fn = make_evaluate(distance_matrix, sorted_nodes, depot, charging_stations,
                                 customer_nodes, max_capacity, energy_consumption_rate,
                                 min_battery_threshold)

    def create_individual():
        customer_seq = random.sample(customer_nodes, len(customer_nodes))
        if random.random() < 0.5:
            station = random.choice(charging_stations)
            if station not in customer_seq:
                customer_seq.insert(random.randint(0, len(customer_seq)), station)
        return creator.Individual(customer_seq)

    toolbox.register("individual", tools.initIterate, creator.Individual, create_individual)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    toolbox.register("mate", tools.cxOrdered)
    toolbox.register("mutate", tools.mutShuffleIndexes, indpb=0.2)
    toolbox.register("select", tools.selTournament, tournsize=3)
    toolbox.register("evaluate", evaluate_fn)

    # ==== Step 4: Run the Genetic Algorithm ====
    population = toolbox.population(n=population_size)
    algorithms.eaSimple(population, toolbox, cxpb=crossover_prob, mutpb=mutation_prob,
                        ngen=num_generations, stats=None, halloffame=None, verbose=False)
    best = tools.selBest(population, k=1)[0]

    best_route = [depot] + best + [depot]
    return best_route
