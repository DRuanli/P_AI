"""
Pacman state and search problem for A* Search
"""


class PacmanState:
    """
    Represents a state in the search space including Pacman's position,
    remaining food and pies, and any special abilities.
    """

    def __init__(self, position, remaining_food, remaining_pies,
                 wall_pass_steps=0, path=None, path_cost=0):
        """
        Initialize a new state

        Args:
            position (tuple): (x, y) position of Pacman
            remaining_food (set): Set of (x, y) positions with food
            remaining_pies (set): Set of (x, y) positions with magical pies
            wall_pass_steps (int): Steps remaining with wall-passing ability
            path (list): List of actions taken to reach this state
            path_cost (int): Cost to reach this state
        """
        self.position = position
        self.remaining_food = remaining_food
        self.remaining_pies = remaining_pies
        self.wall_pass_steps = wall_pass_steps
        self.path = path or []
        self.path_cost = path_cost

    def __eq__(self, other):
        """
        Two states are equal if their position, remaining food/pies, and wall-pass steps are equal
        """
        if not isinstance(other, PacmanState):
            return False

        return (self.position == other.position and
                self.remaining_food == other.remaining_food and
                self.remaining_pies == other.remaining_pies and
                self.wall_pass_steps == other.wall_pass_steps)

    def __hash__(self):
        """
        Hash based on position, remaining food/pies, and wall-pass status
        """
        # Convert sets to frozensets for hashing
        food_hash = frozenset(self.remaining_food)
        pies_hash = frozenset(self.remaining_pies)

        return hash((self.position, food_hash, pies_hash, self.wall_pass_steps))

    def is_goal_state(self):
        """
        Return True if all food has been collected
        """
        return len(self.remaining_food) == 0

    def copy(self):
        """
        Create a deep copy of the state
        """
        return PacmanState(
            self.position,
            self.remaining_food.copy(),
            self.remaining_pies.copy(),
            self.wall_pass_steps,
            self.path.copy(),
            self.path_cost
        )

    def __str__(self):
        """String representation of the state"""
        return (f"Position: {self.position}, "
                f"Food left: {len(self.remaining_food)}, "
                f"Pies left: {len(self.remaining_pies)}, "
                f"Wall-pass steps: {self.wall_pass_steps}, "
                f"Path cost: {self.path_cost}")


class PacmanSearchProblem:
    """
    Defines the A* search problem for Pacman collecting all food
    """

    def __init__(self, maze):
        """
        Initialize the search problem with a maze

        Args:
            maze (Maze): The maze
        """
        self.maze = maze

        # Create initial state
        self.initial_state = PacmanState(
            maze.pacman_start,
            maze.food_positions.copy(),
            maze.magical_pie_positions.copy()
        )

    def get_start_state(self):
        """Return the start state"""
        return self.initial_state

    def is_goal_state(self, state):
        """Return True if state is a goal state"""
        return state.is_goal_state()

    def get_successors(self, state):
        """
        Generate successor states for all legal actions

        Args:
            state (PacmanState): Current state

        Returns:
            list: List of (next_state, action, cost) tuples
        """
        successors = []
        x, y = state.position

        # Check if Pacman can pass through walls
        can_pass_walls = state.wall_pass_steps > 0

        # Get legal moves from current position
        legal_moves = self.maze.get_legal_moves(x, y, can_pass_walls)

        for dx, dy, action in legal_moves:
            # Apply move
            new_x, new_y = x + dx, y + dy

            # Check for teleportation
            teleport_dest = self.maze.get_teleport_destination(new_x, new_y)
            if teleport_dest:
                new_x, new_y = teleport_dest

            # Create new state
            new_state = state.copy()
            new_state.position = (new_x, new_y)

            # Decrease wall-pass steps if active
            if new_state.wall_pass_steps > 0:
                new_state.wall_pass_steps -= 1

            # Check if Pacman collected a food
            if (new_x, new_y) in new_state.remaining_food:
                new_state.remaining_food.remove((new_x, new_y))

            # Check if Pacman collected a magical pie
            if (new_x, new_y) in new_state.remaining_pies:
                new_state.remaining_pies.remove((new_x, new_y))
                new_state.wall_pass_steps = 5  # Reset wall-pass steps to 5

            # Update path and cost
            new_state.path.append(action)
            new_state.path_cost += 1

            # Add successor
            successors.append((new_state, action, 1))

        return successors

    def get_cost_of_actions(self, actions):
        """
        Return the cost of a sequence of actions

        Args:
            actions (list): List of actions

        Returns:
            int: Total cost
        """
        return len(actions)