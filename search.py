"""
A* search algorithm and heuristic functions for Pacman
"""
import heapq
import math


class PriorityQueue:
    """
    Priority queue implementation for A* search
    """

    def __init__(self):
        self.heap = []
        self.count = 0  # Counter for breaking ties

    def push(self, item, priority):
        """Add item to queue with given priority"""
        heapq.heappush(self.heap, (priority, self.count, item))
        self.count += 1

    def pop(self):
        """Remove and return item with lowest priority"""
        return heapq.heappop(self.heap)[2]

    def is_empty(self):
        """Return True if queue is empty"""
        return len(self.heap) == 0


class AStarSearch:
    """
    Implements A* search algorithm for Pacman
    """

    def __init__(self, problem, heuristic):
        """
        Initialize A* search

        Args:
            problem (PacmanSearchProblem): The search problem
            heuristic (function): Heuristic function h(state, problem)
        """
        self.problem = problem
        self.heuristic = heuristic
        self.nodes_expanded = 0

    def search(self):
        """
        Run A* search algorithm

        Returns:
            tuple: (path, actions, cost) where:
                - path is a list of states
                - actions is a list of actions
                - cost is the total cost
        """
        # Initialize data structures
        start_state = self.problem.get_start_state()
        frontier = PriorityQueue()
        explored = set()

        # Add start state to frontier with f = g + h
        g_score = 0  # Cost from start to start is 0
        h_score = self.heuristic.compute(start_state, self.problem)
        f_score = g_score + h_score
        frontier.push(start_state, f_score)

        # Keep track of best g_score for each state
        g_scores = {start_state: 0}

        while not frontier.is_empty():
            # Pop state with lowest f_score
            current_state = frontier.pop()
            self.nodes_expanded += 1

            # Check if goal reached
            if self.problem.is_goal_state(current_state):
                return (self._reconstruct_path(current_state, g_scores),
                        current_state.path,
                        current_state.path_cost)

            # Add to explored set
            explored.add(current_state)

            # Expand state
            for next_state, action, cost in self.problem.get_successors(current_state):
                # Skip if already explored
                if next_state in explored:
                    continue

                # Calculate tentative g_score
                tentative_g_score = current_state.path_cost + cost

                # Skip if we already found a better path to this state
                if next_state in g_scores and tentative_g_score >= g_scores[next_state]:
                    continue

                # This path is the best so far
                g_scores[next_state] = tentative_g_score

                # Calculate f_score and add to frontier
                h_score = self.heuristic.compute(next_state, self.problem)
                f_score = tentative_g_score + h_score
                frontier.push(next_state, f_score)

        # No solution found
        return None, None, float('inf')

    def _reconstruct_path(self, goal_state, g_scores):
        """Reconstruct path from g_scores (only used for visualization)"""
        path = [goal_state]
        return path  # Simplified for this implementation


class Heuristic:
    """Base class for heuristics"""

    def compute(self, state, problem):
        """Compute heuristic value for state"""
        raise NotImplementedError("Subclasses must implement this method")


class NullHeuristic(Heuristic):
    """Zero heuristic for uniform cost search"""

    def compute(self, state, problem):
        return 0


class NearestFoodHeuristic(Heuristic):
    """Manhattan distance to nearest food"""

    def compute(self, state, problem):
        """
        Calculate Manhattan distance to nearest food

        Args:
            state (PacmanState): Current state
            problem (PacmanSearchProblem): The search problem

        Returns:
            float: Heuristic value
        """
        if not state.remaining_food:
            return 0

        x, y = state.position

        # Calculate Manhattan distance to each food
        distances = [abs(x - food_x) + abs(y - food_y)
                     for food_x, food_y in state.remaining_food]

        # Return distance to nearest food
        return min(distances) if distances else 0


class MSTHeuristic(Heuristic):
    """
    Minimum spanning tree heuristic

    Estimates cost to collect all remaining food using a minimum spanning tree
    """

    def compute(self, state, problem):
        """
        Calculate MST-based heuristic

        Args:
            state (PacmanState): Current state
            problem (PacmanSearchProblem): The search problem

        Returns:
            float: Heuristic value
        """
        if not state.remaining_food:
            return 0

        # Include the current position in the nodes
        nodes = list(state.remaining_food)
        nodes.append(state.position)

        # Implement Prim's algorithm for MST
        # Initialize data structures
        n = len(nodes)
        visited = [False] * n
        mst_weight = 0

        # Start from the current position (last node)
        visited[n - 1] = True
        edges_added = 0

        # We need n-1 edges in MST
        while edges_added < n - 1:
            min_dist = float('inf')
            min_u = -1
            min_v = -1

            # Find the minimum weight edge connecting visited and unvisited nodes
            for u in range(n):
                if visited[u]:
                    for v in range(n):
                        if not visited[v]:
                            # Calculate Manhattan distance
                            dist = abs(nodes[u][0] - nodes[v][0]) + abs(nodes[u][1] - nodes[v][1])
                            if dist < min_dist:
                                min_dist = dist
                                min_u = u
                                min_v = v

            # Add the edge to MST
            if min_u != -1 and min_v != -1:
                mst_weight += min_dist
                visited[min_v] = True
                edges_added += 1
            else:
                # No more edges to add (shouldn't happen with a connected graph)
                break

        return mst_weight