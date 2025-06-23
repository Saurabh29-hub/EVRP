import numpy as np
import random
import heapq

def astar(data):
    # ==== Step 1: Extract Data and Prepare Distance Matrix ====
    def extract_data(json_data):
        # === Node Sorting: Depot -> Customer -> Station ===
        node_priority = {'depot': 0, 'customer': 1, 'station': 2}
        sorted_nodes = sorted(json_data['nodes'], key=lambda n: node_priority[n['type']])
        node_id_to_index = {node['id']: idx for idx, node in enumerate(sorted_nodes)}
        
        # === Distance Matrix Initialization ===
        n = len(sorted_nodes)
        distance_matrix = np.full((n, n), np.inf)
        np.fill_diagonal(distance_matrix, 0)

        for edge in json_data['edges']:
            src = node_id_to_index[edge['source']]
            tgt = node_id_to_index[edge['target']]
            dist = edge['distance']
            distance_matrix[src][tgt] = dist
            distance_matrix[tgt][src] = dist  # Assuming symmetric distances

        # === Extract Capacity and Battery Information ===
        vehicle = json_data['vehicles'][0]
        vehicle_capacity = vehicle.get('capacity', 100)
        battery_capacity = vehicle.get('battery_capacity', 200)

        # === Energy & Charging Constraints ===
        constraints = json_data.get('constraints', {})
        energy_rate = constraints.get('energy_consumption_rate', 0.1)

        # === Charging Station Indexes and Ports ===
        charging_stations = []
        charging_ports = {}
        for station in json_data.get('charging_stations', []):
            index = node_id_to_index[station['id']]
            charging_stations.append(index)
            charging_ports[index] = station.get('max_ports', 1)

        # === Customer Demands (pickup, delivery) ===
        customer_demands = {}
        for idx, node in enumerate(sorted_nodes):
            if node['type'] == 'customer':
                customer_demands[idx] = (
                    node.get('pickup', 0),
                    node.get('delivery', 0)
                )

        # === Find Depot Index ===
        depot_idx = next((idx for idx, node in enumerate(sorted_nodes) if node['type'] == 'depot'), 0)

        return {
            "distance_matrix": distance_matrix,
            "vehicle_capacity": vehicle_capacity,
            "battery_capacity": battery_capacity,
            "energy_rate": energy_rate,
            "charging_rate": charging_stations and json_data['charging_stations'][0].get('charging_rate', 50),
            "customer_demands": customer_demands,
            "charging_stations": charging_stations,
            "charging_ports": charging_ports,
            "depot": depot_idx,
            "vehicles": len(json_data.get("vehicles", [])),
            "raw_json": json_data
        }
    
    data = extract_data(data)
    # === Unpack Data ===
    distance_matrix = data["distance_matrix"]
    VEHICLE_CAPACITY = data["vehicle_capacity"]
    BATTERY_CAPACITY = data["battery_capacity"]
    ENERGY_RATE = data["energy_rate"]
    CHARGING_RATE = data["charging_rate"]
    customer_demands = data["customer_demands"]
    charging_stations = data["charging_stations"]
    CHARGING_PORTS = data["charging_ports"]
    depot = data["depot"]
    vehicles = data["vehicles"]

    MIN_CHARGE = 0.15 * BATTERY_CAPACITY
    num_customers = len(customer_demands)

    def heuristic(node, goal):
        return distance_matrix[node][goal]

    def astar(start, goal, distance_matrix):
        open_list, closed_set = [], set()
        heapq.heappush(open_list, (0, start))
        came_from, g_score = {}, {start: 0}

        while open_list:
            _, current = heapq.heappop(open_list)
            if current == goal:
                return reconstruct_path(came_from, current)
            closed_set.add(current)

            for neighbor in range(len(distance_matrix)):
                if distance_matrix[current][neighbor] == np.inf or neighbor in closed_set:
                    continue
                tentative_g = g_score[current] + distance_matrix[current][neighbor]
                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score = tentative_g + heuristic(neighbor, goal)
                    heapq.heappush(open_list, (f_score, neighbor))

        return []

    def reconstruct_path(came_from, current):
        path = [current]
        while current in came_from:
            current = came_from[current]
            path.append(current)
        return path[::-1]

    def optimized_customer_assignment(customers, num_vehicles):
        sorted_customers = sorted(customers, key=lambda c: sum(customer_demands[c]), reverse=True)
        routes = [[] for _ in range(num_vehicles)]
        for i, c in enumerate(sorted_customers):
            routes[i % num_vehicles].append(c)
        return routes

    def get_optimized_routes(customers, num_vehicles):
        vehicle_customers = optimized_customer_assignment(customers, num_vehicles)
        routes = []
        for route in vehicle_customers:
            full_route = [depot] + route + [depot]
            path = []
            for i in range(len(full_route) - 1):
                segment = astar(full_route[i], full_route[i+1], distance_matrix)
                path.extend(segment[:-1])
            path.append(depot)
            routes.append(path)
        return routes

    def simulate_vehicle(route, customer_demands, vehicle_id):
        load, energy, distance, time = 0, BATTERY_CAPACITY, 0, 0
        events, energy_trace, load_trace = [], [], []
        port_wait = {cs: [] for cs in charging_stations}

        total_pickup, total_delivery = 0, 0
        for i in range(len(route) - 1):
            u, v = route[i], route[i + 1]
            dist = distance_matrix[u][v]

            if v in customer_demands:
                pickup, delivery = customer_demands[v]
                load = max(0, load - delivery)
                total_delivery += delivery
                load = min(VEHICLE_CAPACITY, load + pickup)
                total_pickup += pickup

            energy_used = ENERGY_RATE * dist * load
            energy -= energy_used
            distance += dist

            energy_trace.append(energy)
            load_trace.append(load)

            events.append((
                f"Travel {u}->{v}",
                f"Dist={dist}, Delivery={customer_demands.get(v, (0, 0))[1]}, Pickup={customer_demands.get(v, (0, 0))[0]}, Load={load}, Energy Left={energy:.2f}"
            ))

            if energy < MIN_CHARGE:
                nearest_cs = min(charging_stations, key=lambda cs: distance_matrix[v][cs])
                to_cs = distance_matrix[v][nearest_cs]
                energy -= ENERGY_RATE * to_cs * load
                distance += to_cs
                wait = max(0, len(port_wait[nearest_cs]) - CHARGING_PORTS[nearest_cs])
                charge_amount = BATTERY_CAPACITY - energy
                charge_time = charge_amount / CHARGING_RATE
                time += wait + charge_time
                energy = BATTERY_CAPACITY
                energy_trace.append(energy)
                load_trace.append(load)
                events.append((f"Charge at {nearest_cs}", f"Wait={wait}, Charged={charge_amount:.2f}, Time={charge_time:.1f}"))

        return {
            "vehicle": vehicle_id,
            "total_pickup": total_pickup,
            "total_delivery": total_delivery,
            "route": route,
            "distance": distance,
            "events": events,
            "final_energy": energy,
            "final_load": load,
            "time": time,
            "energy_trace": energy_trace,
            "load_trace": load_trace
        }

    # === Run Simulation ===
    customers = list(customer_demands.keys())
    routes = get_optimized_routes(customers, vehicles)

    # for i, route in enumerate(routes):
    #     sim = simulate_vehicle(route, customer_demands, i+1)
    #     print(f"\nVehicle {sim['vehicle']} Route: {sim['route']}")
    #     for event in sim['events']:
    #         print(f"  {event[0]} --> {event[1]}")
    #     print(f"Total Distance: {sim['distance']:.2f}, Final Load: {sim['final_load']}, Final Energy: {sim['final_energy']:.2f}, Total Time: {sim['time']:.2f}")
    #     print(f"Total Pickup: {sim['total_pickup']}, Total Delivery: {sim['total_delivery']}")

    # Get node index → "type-id" mapping using sorted node list
    node_priority = {'depot': 0, 'customer': 1, 'station': 2}
    sorted_nodes = sorted(data["raw_json"]['nodes'], key=lambda n: node_priority[n['type']])
    index_to_label = {idx: node['id'] for idx, node in enumerate(sorted_nodes)}

    output = []
    for i, route in enumerate(routes):
        path = [index_to_label[node] for node in route]
        output.append({
            "vehicleId": f"EV-{i+1}",
            "path": path
        })
    print("output")
    print(output)
    return output


