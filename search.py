import heapq
from pacman import PacmanState


class PriorityQueue:
    def __init__(self):
        self.heap = []
        self.count = 0  # For breaking ties consistently

    def push(self, item, priority):
        entry = (priority, self.count, item)
        heapq.heappush(self.heap, entry)
        self.count += 1

    def pop(self):
        _, _, item = heapq.heappop(self.heap)
        return item

    def is_empty(self):
        return len(self.heap) == 0


def manhattan_distance(pos1, pos2):
    """Calculate Manhattan distance between two positions"""
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])


def min_food_distance_heuristic(position, food_points):
    """
    Heuristic: Minimum Manhattan distance to any food point

    Admissibility: This is admissible because the Manhattan distance is the minimum
    possible number of steps needed to reach any food point in a grid world without walls.
    Since we can't reach a goal state without visiting each food point, this never overestimates.

    Consistency: For any two adjacent states, the change in heuristic value is at most 1,
    which is less than or equal to the cost of the action (1).
    """
    if not food_points:
        return 0

    # Convert to a list if it's a set to avoid iteration issues
    food_list = list(food_points)
    if not food_list:
        return 0

    return min(manhattan_distance(position, food) for food in food_list)


def mst_heuristic(position, food_points):
    """
    Heuristic: Minimum Spanning Tree

    Creates a minimum spanning tree connecting Pacman and all food points.
    The length of this tree is an admissible estimate of the minimum path
    needed to collect all food.

    Admissibility: This heuristic never overestimates because the MST represents
    the minimum possible length of a tree connecting all points, which must be
    less than or equal to the length of any tour that visits all points.

    Consistency: For any states s and s', where s' is reached from s by an action with cost c,
    h(s) ≤ h(s') + c, because removing a food point from the MST can only reduce the total
    distance by at most the distance traveled in one step.
    """
    if not food_points:
        return 0

    # Convert to a list if it's a set to avoid iteration issues
    food_list = list(food_points)
    if not food_list:
        return 0

    # Include pacman's position and all food points
    all_points = [position] + food_list
    num_points = len(all_points)

    if num_points == 1:  # Only Pacman, no food
        return 0

    # Calculate distances between all points
    distances = {}
    for i in range(num_points):
        for j in range(i + 1, num_points):
            distances[(i, j)] = manhattan_distance(all_points[i], all_points[j])
            distances[(j, i)] = distances[(i, j)]  # Symmetric

    # Prim's algorithm to find MST
    mst_cost = 0
    visited = {0}  # Start with Pacman's position

    while len(visited) < num_points:
        min_edge = float('inf')
        next_node = None

        # Find the cheapest edge from any visited node to an unvisited node
        for i in visited:
            for j in range(num_points):
                if j not in visited:
                    if distances[(i, j)] < min_edge:
                        min_edge = distances[(i, j)]
                        next_node = j

        if next_node is not None:
            mst_cost += min_edge
            visited.add(next_node)
        else:
            break  # Should not happen in a connected graph

    return mst_cost


def a_star_search(maze, heuristic_func=min_food_distance_heuristic):
    """
    A* search algorithm to find the optimal path for Pacman to collect all food.

    Args:
        maze: The maze object containing the layout information
        heuristic_func: The heuristic function to use for A* search

    Returns:
        tuple: (actions, cost) where actions is a list of directions and cost is the total path cost
    """
    # Initialize the starting state
    initial_food = set(maze.food_points)
    initial_magical_pies = set(maze.magical_pies)

    initial_state = PacmanState(
        position=maze.pacman_start,
        remaining_food=initial_food,
        remaining_magical_pies=initial_magical_pies
    )

    # Initialize the frontier with the starting state
    frontier = PriorityQueue()
    frontier.push(initial_state, 0)  # Priority is 0 for starting state

    # Set to keep track of explored states
    explored = set()

    # Dictionary to keep track of best g-value for each state
    g_values = {initial_state: 0}

    # Debug info
    states_explored = 0

    while not frontier.is_empty():
        # Get the state with the lowest f-value from the frontier
        current_state = frontier.pop()
        states_explored += 1

        # If we've reached a goal state, return the solution
        if current_state.is_goal():
            print(f"Solution found after exploring {states_explored} states!")
            return current_state.actions, current_state.cost

        # Add the current state to the explored set
        explored.add(current_state)

        # Get successor states
        successor_states = current_state.get_successor_states(maze)

        for successor in successor_states:
            # Calculate the g-value (cost so far) for this successor
            g_value = successor.cost

            # Skip if this state is already explored and we didn't find a better path
            if successor in explored and g_value >= g_values.get(successor, float('inf')):
                continue

            # If this is a new state or we found a better path to it
            if successor not in g_values or g_value < g_values[successor]:
                g_values[successor] = g_value

                # Calculate h-value based on the chosen heuristic
                h_value = heuristic_func(successor.position, successor.remaining_food)

                # Calculate f-value = g-value + h-value
                f_value = g_value + h_value

                # Add to frontier with f-value as priority
                frontier.push(successor, f_value)

    # If we exhausted the frontier without finding a solution
    print(f"No solution found after exploring {states_explored} states.")
    return None, 0