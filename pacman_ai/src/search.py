import heapq
from typing import Tuple, Set, List, Dict, Optional, Callable, Any
from pacman import PacmanState


class PriorityQueue:
    """Priority queue for A* frontier management with consistent tie-breaking."""

    def __init__(self):
        self.heap = []
        self.count = 0

    def push(self, item: Any, priority: float) -> None:
        heapq.heappush(self.heap, (priority, self.count, item))
        self.count += 1

    def pop(self) -> Any:
        return heapq.heappop(self.heap)[2]

    def is_empty(self) -> bool:
        return not self.heap


def manhattan_distance(pos1: Tuple[int, int], pos2: Tuple[int, int]) -> int:
    """Calculate Manhattan distance between two grid positions."""
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

def mst_heuristic(position: Tuple[int, int], food_points: Set[Tuple[int, int]]) -> int:
    """
    Minimum Spanning Tree heuristic for multi-point collection.

    Creates MST connecting Pacman and all food. The tree length is an admissible
    estimate of minimum path needed to collect all food.
    """
    if not food_points: return 0

    all_points = [position] + list(food_points)
    if len(all_points) == 1: return 0

    # Calculate pairwise distances
    distances = {}
    for i, p1 in enumerate(all_points):
        for j in range(i + 1, len(all_points)):
            dist = manhattan_distance(p1, all_points[j])
            distances[(i, j)] = distances[(j, i)] = dist

    # Prim's algorithm for MST
    mst_cost, visited = 0, {0}

    while len(visited) < len(all_points):
        min_edge, next_node = float('inf'), None

        for i in visited:
            for j in range(len(all_points)):
                if j not in visited and distances[(i, j)] < min_edge:
                    min_edge, next_node = distances[(i, j)], j

        if next_node is not None:
            mst_cost += min_edge
            visited.add(next_node)
        else:
            break

    return mst_cost


def a_star_search(maze, heuristic_func: Callable = mst_heuristic, logger=None) -> Tuple[Optional[List[str]], int]:
    """
    A* search for optimal path to collect all food in maze.

    Params:
        maze: Maze object with layout and game mechanics
        heuristic_func: Heuristic for A* search (mfd or mst)
        logger: Optional logger for search progress

    Returns:
        (actions, cost): List of directions and total path cost
    """
    # Initialize with starting state
    initial_state = PacmanState(
        position=maze.pacman_start,
        remaining_food=set(maze.food_points),
        remaining_magical_pies=set(maze.magical_pies)
    )

    frontier = PriorityQueue()
    frontier.push(initial_state, 0)
    explored = set()
    g_values = {initial_state: 0}
    states_explored = max_frontier_size = 0

    if logger:
        logger.info(f"A* search started from position {maze.pacman_start}")
        logger.info(f"Number of food points: {len(maze.food_points)}")
        logger.info(f"Number of magical pies: {len(maze.magical_pies)}")

    while not frontier.is_empty():
        current_state = frontier.pop()
        states_explored += 1

        if logger and states_explored % 1000 == 0:
            logger.info(f"States explored: {states_explored}, current position: {current_state.position}, " +
                        f"remaining food: {len(current_state.remaining_food)}")

        if current_state.is_goal():
            if logger:
                logger.info(f"Solution found after exploring {states_explored} states")
                logger.info(f"Max frontier size: {max_frontier_size}")
            print(f"Solution found after exploring {states_explored} states!")
            return current_state.actions, current_state.cost

        explored.add(current_state)

        for successor in current_state.get_successor_states(maze):
            g_value = successor.cost

            if successor in explored and g_value >= g_values.get(successor, float('inf')):
                continue

            if successor not in g_values or g_value < g_values[successor]:
                g_values[successor] = g_value
                h_value = heuristic_func(successor.position, successor.remaining_food)
                frontier.push(successor, g_value + h_value)
                max_frontier_size = max(max_frontier_size, len(frontier.heap))

    if logger:
        logger.warning(f"No solution found after exploring {states_explored} states")
    print(f"No solution found after exploring {states_explored} states.")
    return None, 0