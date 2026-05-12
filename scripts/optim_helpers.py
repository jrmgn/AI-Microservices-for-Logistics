from ortools.constraint_solver import pywrapcp, routing_enums_pb2

def solve_tsp(distance_matrix):
    n = len(distance_matrix)
    manager = pywrapcp.RoutingIndexManager(n, 1, 0) 
    routing = pywrapcp.RoutingModel(manager)

    def dist_callback(i, j):
        return int(distance_matrix[manager.IndexToNode(i)][manager.IndexToNode(j)])

    transit_callback_index = routing.RegisterTransitCallback(dist_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
    solution = routing.SolveWithParameters(search_parameters)
    if solution:
        idx = routing.Start(0)
        route = []
        while not routing.IsEnd(idx):
            route.append(manager.IndexToNode(idx))
            idx = solution.Value(routing.NextVar(idx))
        route.append(manager.IndexToNode(idx))
        return route
    else:
        return None
    

def solve_vrp(distance_matrix, demands, vehicle_capacities):
    n = len(distance_matrix)
    num_vehicles = len(vehicle_capacities)
    manager = pywrapcp.RoutingIndexManager(n, num_vehicles, 0)
    routing = pywrapcp.RoutingModel(manager)

    def dist_callback(i, j):
        return int(distance_matrix[manager.IndexToNode(i)][manager.IndexToNode(j)])

    transit_callback_index = routing.RegisterTransitCallback(dist_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    def demand_callback(index):
        node = manager.IndexToNode(index)
        return demands[node]
    
    demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
    routing.AddDimensionWithVehicleCapacity(
        demand_callback_index,
        0,  
        vehicle_capacities,  
        True,  
        "Capacity")

    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
    
    solution = routing.SolveWithParameters(search_parameters)
    if not solution:
        return None
    
    routes = []
    for v in range(num_vehicles):
        idx = routing.Start(v)
        r = []
        while not routing.IsEnd(idx):
            r.append(manager.IndexToNode(idx))
            idx = solution.Value(routing.NextVar(idx))
        r.append(manager.IndexToNode(idx))
        routes.append(r)
    return routes