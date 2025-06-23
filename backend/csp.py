from z3 import *
import json
import re

def safe_float(z3_decimal_str):
    """Converts a Z3 decimal string like '10.09?' to float safely."""
    return float(re.sub(r'[?]', '', z3_decimal_str))

def convert_input_to_format(input_data):
    # Extract vehicle details from list
    num_vehicles = len(input_data['vehicles'])
    max_energy = input_data['vehicles'][0]['battery_capacity']
    max_load = input_data['vehicles'][0]['capacity']
    max_energy = 100 #hardcoded
    max_load = 100 #hardcoded
    # Node indexing
    node_id_to_index = {node['id']: idx for idx, node in enumerate(input_data['nodes'])}
    depot = node_id_to_index[next(node['id'] for node in input_data['nodes'] if node['type'] == 'depot')]
    
    # Charging station handling
    charging_stations = [node_id_to_index[cs['id']] for cs in input_data['charging_stations']]
    charging_rate = input_data['charging_stations'][0]['charging_rate']
    charging_ports = input_data['charging_stations'][0]['max_ports']
    
    # Energy parameters
    min_energy_threshold = int(max_energy * input_data['constraints']['min_battery_threshold'])
    energy_consumption_rate = input_data['constraints']['energy_consumption_rate']
    
    # Modified distance matrix creation with 0 distance check
    full_distance_matrix = {}
    for edge in input_data['edges']:
        distance = edge['distance']
        if distance <= 0:  # Skip zero or negative distances
            continue
        i = node_id_to_index[edge['source']]
        j = node_id_to_index[edge['target']]
        full_distance_matrix[(i, j)] = distance
        full_distance_matrix[(j, i)] = distance  # Add reverse direction
    
    # Customer demands extraction
    customer_demands = {
        node_id_to_index[node['id']]: {'pickup': node.get('pickup', 0), 'delivery': node.get('delivery', 0)}
        for node in input_data['nodes'] if node['type'] == 'customer'
    }

    return {
        'num_vehicles': num_vehicles,
        'num_nodes': len(input_data['nodes']),
        'depot': depot,
        'charging_stations': charging_stations,
        'max_energy': max_energy,
        'min_energy_threshold': min_energy_threshold,
        'max_load': max_load,
        'energy_consumption_rate': energy_consumption_rate,
        'charging_rate': charging_rate,
        'charging_ports': charging_ports,
        'distance_matrix': full_distance_matrix,
        'customer_demands': customer_demands
    }


def csp_z3(data):
    #print("Inside csp")
    #return {"hi": "csp"}
    op_data = convert_input_to_format(data)
    #print(op_data)
    num_vehicles = op_data['num_vehicles']
    num_nodes = op_data['num_nodes']
    depot = op_data['depot']
    charging_stations = op_data['charging_stations']
    max_energy = op_data['max_energy']
    min_energy_threshold = (max_energy*15)//100
    max_load = op_data['max_load']
    energy_consumption_rate = 0.5
    charging_rate = 5
    charging_ports = 1

    distance_matrix = op_data['distance_matrix']

    full_distance_matrix = {}
    for (i, j), dist in distance_matrix.items():
        full_distance_matrix[(i, j)] = dist
        full_distance_matrix[(j, i)] = dist

    customer_demands = op_data['customer_demands']

    customer_nodes = list(customer_demands.keys())

    solver = Optimize()
    
    # Decision Variables(3d matrix. x_{2}_{3}_{4} = 1 means vehicle 2 goes from 3 to 4 
    # and that path may or may not exist. If the path exist and vehicle 2 takes the path
    # then for that path energy/battery will be decreased)
    x = []
    for v in range(num_vehicles):
        v_routes = []
        for i in range(num_nodes):
            n_routes = []
            for j in range(num_nodes):
                # Create a boolean variable for each vehicle's route between nodes
                temp_route_var = Bool(f'x_{v}_{i}_{j}')
                n_routes.append(temp_route_var)
            v_routes.append(n_routes)
        x.append(v_routes)
    #print(x)

    # Battery level(2d matrix, energy_2_5 = 100 -- battery level of vehicle 2 when it arrives at node 5)
    energy = []
    for v in range(num_vehicles):
        t1 = []
        for node in range(num_nodes):
            temp = Real(f'energy_{v}_{node}')
            t1.append(temp)
        energy.append(t1)
    #print(energy)

    # load(2d matrix, load_2_5 = 100 -- load of vehicle 2 when it arrives at node 5)
    load = []
    for v in range(num_vehicles):
        t1 = []
        for node in range(num_nodes):
            temp = Real(f'load_{v}_{node}')
            t1.append(temp)
        load.append(t1)
    #print(load)
    
    charging_time = []
    for v in range(num_vehicles):
        t1 = []
        for node in range(num_nodes):
            temp = Real(f'charging_time_{v}_{node}')
            t1.append(temp)
        charging_time.append(t1)
    #print(charging_time)
    
    # NEW: Partial Pickup and Delivery Variables
    #pickup_amount = [[Real(f'pickup_amount_{v}_{i}') for i in range(num_nodes)] for v in range(num_vehicles)]
    #print(pickup_amount)
    
    pickup_amount = []
    for v in range(num_vehicles):
        t1 = []
        for node in range(num_nodes):
            temp = Int(f'pickup_amount_{v}_{node}')
            t1.append(temp)
        pickup_amount.append(t1)
    #print(pickup_amount)

    # delivery_amount = [[Real(f'delivery_{v}_{i}') for i in range(num_nodes)] for v in range(num_vehicles)]
    # print(delivery_amount)
    delivery_amount = []
    for v in range(num_vehicles):
        t1 = []
        for node in range(num_nodes):
            temp = Int(f'delivery_amount_{v}_{node}')
            t1.append(temp)
        delivery_amount.append(t1)
    #print(delivery_amount)

    # Constraints
    
    for v in range(num_vehicles):
        for i in range(num_nodes):
            for j in range(num_nodes):
                if i != j and (i, j) not in full_distance_matrix:
                    solver.add(x[v][i][j] == False)
    # 1.a. Flow Conservation: Every customer (excluding depot & charging stations) must be visited and exited by a vehicle
    for v in range(num_vehicles):
        for i in range(1, num_nodes):  # Exclude depot but include all other nodes
            if i not in charging_stations:  # apply this only to customer nodes except itself
                solver.add(Sum([x[v][j][i] for j in range(num_nodes) if j != i]) >= 1)

    # 1.b. node constraint. For every node(includeing depot & charging stations) the number of incoming edges equals the number of outgoing edges 
    for v in range(num_vehicles):
        for i in range(num_nodes):  # Include all nodes (depot, customers, charging stations)
            solver.add(
                Sum([x[v][j][i] for j in range(num_nodes) if j != i]) == Sum([x[v][i][k] for k in range(num_nodes) if k != i])
            )
    
    # 1.c. Each vehicle starts and ends at depot(depot constraint)
    for v in range(num_vehicles):
        solver.add(Sum([x[v][depot][j] for j in range(1, num_nodes)]) == 1)
        solver.add(Sum([x[v][j][depot] for j in range(1, num_nodes)]) == 1)


    # 2.a. Partial Pickup and Delivery Constraints
    # Modified Constraints Section (Lines 128-133)
    for v in range(num_vehicles):
        for customer_node in customer_demands.keys():  # Only iterate through defined customers
            i = customer_node
            solver.add(0 <= pickup_amount[v][i])
            solver.add(pickup_amount[v][i] <= customer_demands[i]['pickup'])
            
            solver.add(0 <= delivery_amount[v][i])
            solver.add(delivery_amount[v][i] <= customer_demands[i]['delivery'])

    # 2.b. Vehicle Load Constraints
    for v in range(num_vehicles):
        for i in range(num_nodes):
            solver.add(load[v][i] >= 0)
            solver.add(load[v][i] <= max_load)
    
    # 3. complex logic (vehicle v is going from node i to j)
    for v in range(num_vehicles):
        for i in range(num_nodes):
            for j in range(num_nodes):
                if i != j and (i, j) in distance_matrix:
                    # retrieves the remaining pickup and delivery demands at node j
                    remaining_pickup = customer_demands.get(j, {}).get('pickup', 0)
                    remaining_delivery = customer_demands.get(j, {}).get('delivery', 0)
                    
                    # Calculate available space and energy constraints
                    available_pickup_space = max_load - pickup_amount[v][i] #Calculates how much space is available in the vehicle v for additional pickups 
                    available_delivery_space = pickup_amount[v][i]
                    
                    # Energy needed calculation
                    # total_load = pickup_amount[v][i] + remaining_pickup
                    total_load = pickup_amount[v][i]
                    energy_needed = energy_consumption_rate * distance_matrix[(i, j)] * total_load
                    
                    # Feasibility checks
                    max_feasible_pickup = If(energy[v][i] - energy_needed >= min_energy_threshold, 
                                            remaining_pickup, 0)
                    max_feasible_delivery = If(energy[v][i] - energy_needed >= min_energy_threshold, 
                                            remaining_delivery, 0)
                    
                    # Calculate actual pickup and delivery amounts
                    """In simple language: If vehicle travels from i to j:
                        If remaining pickup < available space:
                            If remaining pickup < max feasible pickup:
                                Actual pickup = remaining pickup.
                            Else:
                                Actual pickup = max feasible pickup.
                        Else:  # Remaining pickup exceeds available space
                            If available space < max feasible pickup:
                                Actual pickup = available space.
                            Else:
                                Actual pickup = max feasible pickup.
                    Else:
                        Actual pickup = 0.
                    """
                    actual_pickup = If(x[v][i][j], 
                   If(remaining_pickup < available_pickup_space, If(remaining_pickup < max_feasible_pickup, remaining_pickup, max_feasible_pickup),
                      If(available_pickup_space < max_feasible_pickup, available_pickup_space, max_feasible_pickup)), 
                   0)


                    actual_delivery = If(x[v][i][j], 
                     If(remaining_delivery < available_delivery_space, 
                        If(remaining_delivery < max_feasible_delivery, remaining_delivery, max_feasible_delivery),
                        If(available_delivery_space < max_feasible_delivery, available_delivery_space, max_feasible_delivery)), 
                     0)

                    
                    # load constraints
                    solver.add(Implies(x[v][i][j], 
                        And(
                            pickup_amount[v][j] == pickup_amount[v][i] + actual_pickup,
                            delivery_amount[v][j] == delivery_amount[v][i] + actual_delivery,
                            load[v][j] == load[v][i] + pickup_amount[v][j] - delivery_amount[v][j]
                        )
                    ))

    
    # 4. Energy Consumption Constraints
    for v in range(num_vehicles):
        solver.add(energy[v][depot] == max_energy) # Vehicles start at the depot with full energy.
        for i in range(num_nodes):
            for j in range(num_nodes):
                if i != j and (i, j) in distance_matrix:
                    distance = distance_matrix[(i, j)]
                    energy_consumed = energy_consumption_rate * distance * load[v][i]
                    solver.add(Implies(x[v][i][j], energy[v][j] == energy[v][i] - energy_consumed))
                    solver.add(energy[v][j] >= min_energy_threshold)

    
    # 5. Charging Station Constraints (Limit Vehicles Charging Simultaneously)
    for charging_station in charging_stations:
        solver.add(Sum([Sum([charging_time[v][charging_station] for v in range(num_vehicles)])]) <= charging_ports)

    # 6. Waiting Time at Charging Stations (Handled Implicitly)
    for v in range(num_vehicles):
        for charging_station in charging_stations:
            solver.add(charging_time[v][charging_station] >= 0)
    
    # 7. Charging Time Proportional to Energy Needed
    for v in range(num_vehicles):
        for charging_station in charging_stations:
            solver.add(charging_time[v][charging_station] == (max_energy - energy[v][charging_station]) / charging_rate)
    
    # Objective Function: Minimize Total Distance + Energy Usage
    total_distance = Sum([
        If(x[v][i][j], distance_matrix.get((i, j), 0), 0)
        for v in range(num_vehicles) for i in range(num_nodes) for j in range(num_nodes)
    ])
    total_energy_used = Sum([
        energy[v][i] for v in range(num_vehicles) for i in range(num_nodes)
    ])
    total_charging_time = Sum([
        charging_time[v][node] for v in range(num_vehicles) for node in charging_stations
    ])
    solver.minimize(total_distance + total_energy_used +total_charging_time)

    if solver.check() == sat:
        model = solver.model()
        print("Solution Found:")
        total_distance = 0
        total_energy = 0
        vehicle_routes = {}
        for v in range(num_vehicles):
            print(f"\nVehicle {v} Route:")
            current_node = depot
            visited = [depot]
            while True:
                next_node = None
                for j in range(num_nodes):
                    if j != current_node and is_true(model.evaluate(x[v][current_node][j])):
                        next_node = j
                        break
                if next_node is None or next_node in visited:
                    break
                visited.append(next_node)
                ce = model.evaluate(energy[v][current_node]).as_decimal(5)
                ne = model.evaluate(energy[v][next_node]).as_decimal(5)
                cl = model.evaluate(load[v][current_node]).as_decimal(5)
                nl = model.evaluate(load[v][next_node]).as_decimal(5)
                pickup_val = model.evaluate(pickup_amount[v][next_node]) if next_node in customer_demands else 0
                delivery_val = model.evaluate(delivery_amount[v][next_node]) if next_node in customer_demands else 0
                dist_val = full_distance_matrix.get((current_node, next_node), 0)
                energy_used = safe_float(ce) - safe_float(ne)
                total_distance += dist_val
                total_energy += energy_used
                print(f"  From Node {current_node} → Node {next_node}")
                print(f"    Action: Pickup {pickup_val}, Delivery {delivery_val}")
                print(f"    Energy: {ce} → {ne}")
                print(f"    Load: {cl} → {nl}")
                if next_node in charging_stations:
                    charging_duration = model.evaluate(charging_time[v][next_node]).as_decimal(2)
                    print(f"    Charging Time: {charging_duration}")
                current_node = next_node
            print(f"Vehicle {v} route completed.\n")
            vehicle_routes[f'vehicle_{v}'] = visited

        # print(f"Total Distance: {total_distance}")
        # print(f"Total Energy Used: {total_energy:.2f}")
        # vehicle_routes['total_distance'] = total_distance
        # vehicle_routes['total_energy'] = total_energy
        # # Export to JSON format
        # print("\nJSON Output of Routes:")
        # print(json.dumps(vehicle_routes, indent=2))
        
        # New output format
                # New output format
        output_routes = []
        for v in range(num_vehicles):
            route = vehicle_routes[f'vehicle_{v}']
            path = []
            for node in route:
                if node == depot:
                    label = f"depot-{depot}"
                elif node in charging_stations:
                    label = f"station-{node}"
                elif node in customer_demands:
                    label = f"customer-{node}"
                else:
                    label = f"node-{node}"  # fallback
                path.append(label)

            # Ensure the route ends with depot
            if path[-1] != f"depot-{depot}":
                path.append(f"depot-{depot}")

            output_routes.append({
                "vehicleId": f"EV-{v+1}",
                "path": path
            })

        # print(json.dumps(output_routes, indent=2))
        return output_routes

    else:
        print("No solution exists or the solver timed out.")
        vehicle_routes['no_sol'] = 'No Solution Found'
        print(json.dumps(vehicle_routes, indent=2))

    #solve_evrp()

    print(vehicle_routes)
    return vehicle_routes