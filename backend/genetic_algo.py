import numpy as np
import random
from deap import base, creator, tools, algorithms

def genetic_algo(data):
    # === 1. Parse JSON ===
    node_ids = [node['id'] for node in data['nodes']]
    node_index = {node_id: i for i, node_id in enumerate(node_ids)}
    index_node = {i: node_id for node_id, i in node_index.items()}
    num_nodes = len(node_ids)

    depot_id = [node for node in data['nodes'] if node['type'] == 'depot'][0]['id']
    depot_index = node_index[depot_id]

    customers = [node for node in data['nodes'] if node['type'] == 'customer']
    charging_stations = [node for node in data['nodes'] if node['type'] == 'station']

    customer_indices = [node_index[cust['id']] for cust in customers]
    charging_indices = [node_index[station['id']] for station in charging_stations]

    pickup = {node_index[c['id']]: c['pickup'] for c in customers}
    delivery = {node_index[c['id']]: c['delivery'] for c in customers}

    # === 2. Distance Matrix ===
    distance_matrix = np.full((num_nodes, num_nodes), np.inf)
    np.fill_diagonal(distance_matrix, 0)
    for edge in data['edges']:
        src = node_index[edge['source']]
        tgt = node_index[edge['target']]
        dist = edge['distance']
        distance_matrix[src][tgt] = dist
        distance_matrix[tgt][src] = dist

    # === 3. Vehicle and Constraints ===
    vehicles = data['vehicles']
    num_vehicles = len(vehicles)
    max_capacity = vehicles[0]['capacity']
    max_energy = vehicles[0]['battery_capacity']

    energy_consumption_rate = data['constraints']['energy_consumption_rate']
    min_energy_threshold = data['constraints']['min_battery_threshold'] * max_energy

    num_generations = 100
    population_size = 50
    mutation_prob = 0.2
    crossover_prob = 0.7

    # === 4. DEAP Setup ===
    def safe_creator(name, base_class, **kwargs):
        if name not in creator.__dict__:
            creator.create(name, base_class, **kwargs)

    safe_creator("FitnessMin", base.Fitness, weights=(-1.0,))
    safe_creator("Individual", list, fitness=creator.FitnessMin)

    toolbox = base.Toolbox()

    def create_individual():
        cust_list = customer_indices[:]
        random.shuffle(cust_list)
        split = np.array_split(cust_list, num_vehicles)
        return creator.Individual([list(route) for route in split])

    toolbox.register("individual", tools.initIterate, creator.Individual, create_individual)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)

    def evaluate(individual):
        total_distance = 0
        for vehicle_route in individual:
            energy = max_energy
            load = 0
            prev = depot_index
            for node in vehicle_route:
                dist = distance_matrix[prev][node]
                if dist == np.inf:
                    return 9999,

                total_distance += dist
                energy -= dist * energy_consumption_rate
                load += pickup.get(node, 0)
                load -= delivery.get(node, 0)

                if energy < min_energy_threshold:
                    if node in charging_indices:
                        energy = max_energy
                    else:
                        return 9999,
                if load < 0 or load > max_capacity:
                    return 9999,
                prev = node

            total_distance += distance_matrix[prev][depot_index]
        return total_distance,

    toolbox.register("mate", tools.cxTwoPoint)
    toolbox.register("mutate", tools.mutShuffleIndexes, indpb=0.2)
    toolbox.register("select", tools.selTournament, tournsize=3)
    toolbox.register("evaluate", evaluate)

    # === 5. Run GA ===
    def run_ga():
        pop = toolbox.population(n=population_size)
        algorithms.eaSimple(pop, toolbox, cxpb=crossover_prob, mutpb=mutation_prob,
                            ngen=num_generations, stats=None, halloffame=None, verbose=False)
        return tools.selBest(pop, k=1)[0]

    best = run_ga()

    # === 6. Print Detailed Route Breakdown ===
    print("\n=== Detailed Route Breakdown ===")
    for i, route in enumerate(best):
        vehicle_id = vehicles[i]['id'] if i < len(vehicles) else f"Vehicle-{i+1}"
        print(f"\nVehicle {i+1} ({vehicle_id}) Route: {[depot_id] + [index_node[n] for n in route] + [depot_id]}")
        energy = max_energy
        load = 0
        total_distance = 0
        total_pickup = 0
        total_delivery = 0
        prev = depot_index

        for node in route:
            dist = distance_matrix[prev][node]
            energy -= dist * energy_consumption_rate
            load += pickup.get(node, 0)
            total_pickup += pickup.get(node, 0)
            load -= delivery.get(node, 0)
            total_delivery += delivery.get(node, 0)
            print(f"  Travel {index_node[prev]} -> {index_node[node]} --> Dist={dist}, "
                  f"Delivery={delivery.get(node, 0)}, Pickup={pickup.get(node, 0)}, "
                  f"Load={load}, Energy Left={energy:.2f}")
            if energy < min_energy_threshold and node in charging_indices:
                energy = max_energy
                print(f"    ⚡ Recharged at {index_node[node]} --> Energy Restored to {energy}")
            prev = node

        dist_back = distance_matrix[prev][depot_index]
        energy -= dist_back * energy_consumption_rate
        total_distance += dist_back
        print(f"  Travel {index_node[prev]} -> {depot_id} --> Dist={dist_back}, Delivery=0, Pickup=0, Load={load}, Energy Left={energy:.2f}")
        print(f"  Total Distance: {total_distance}, Final Load: {load}, Final Energy: {energy:.2f}")
        print(f"  Total Pickup: {total_pickup}, Total Delivery: {total_delivery}")

    # === 7. Build Return Output ===
    results = []
    for i, route in enumerate(best):
        vehicle_id = vehicles[i]['id'] if i < len(vehicles) else f"Vehicle-{i+1}"
        full_path = [depot_index] + route + [depot_index]
        path_ids = [index_node[idx] for idx in full_path]
        results.append({
            "vehicleId": vehicle_id,
            "path": path_ids
        })

    return results
