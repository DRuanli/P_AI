class PacmanState:
    """
    Represents a state in the Pacman search problem, tracking position,
    remaining food/pies, wall status, and path information.
    """

    def __init__(self, position: tuple, remaining_food: set, remaining_magical_pies: set,
                 walls_vanished_steps: int = 0, actions: list = None, cost: int = 0):
        self.position = position  # (x, y) coordinates
        self.remaining_food = set(remaining_food)
        self.remaining_magical_pies = set(remaining_magical_pies)
        self.walls_vanished_steps = walls_vanished_steps  # Steps walls remain vanished (0-5)
        self.actions = actions or []  # Actions taken to reach this state
        self.cost = cost  # Total path cost (steps)

    def __eq__(self, other) -> bool:
        """Compare states based on position, remaining collectibles, and wall status"""
        if not isinstance(other, PacmanState): return False
        return (self.position == other.position and
                self.remaining_food == other.remaining_food and
                self.remaining_magical_pies == other.remaining_magical_pies and
                self.walls_vanished_steps == other.walls_vanished_steps)

    def __hash__(self) -> int:
        """Hash function for use in sets and dictionaries"""
        return hash((self.position, frozenset(self.remaining_food),
                     frozenset(self.remaining_magical_pies), self.walls_vanished_steps))

    def is_goal(self) -> bool:
        """Check if all food has been collected"""
        return not self.remaining_food

    def are_walls_vanished(self) -> bool:
        """Check if walls are currently passable"""
        return self.walls_vanished_steps > 0

    def get_successor_states(self, maze) -> list:
        """
        Generate all valid successor states from current position.

        Applies movement rules, teleportation at corners, food collection,
        and magical pie effects.

        Params:
            maze: Maze object containing layout and movement rules

        Returns:
            List of valid PacmanState successors
        """
        successors = []
        x, y = self.position

        for action, (new_x, new_y) in maze.get_valid_moves(x, y, self.are_walls_vanished()):
            # Skip invalid wall movements
            if maze.is_wall(new_x, new_y) and not self.are_walls_vanished(): continue

            # Calculate wall vanish duration after this move
            new_vanish_steps = max(0, self.walls_vanished_steps - 1) if action != 'Stop' else self.walls_vanished_steps

            # Prevent getting trapped in walls
            if maze.is_wall(new_x, new_y) and new_vanish_steps == 0: continue

            # Create successor state
            new_state = PacmanState(
                position=(new_x, new_y),
                remaining_food=self.remaining_food.copy(),
                remaining_magical_pies=self.remaining_magical_pies.copy(),
                walls_vanished_steps=new_vanish_steps,
                actions=self.actions + [action],
                cost=self.cost + (0 if action == 'Stop' else 1)
            )

            # Handle teleportation at corners
            if maze.is_corner(new_x, new_y):
                teleport_pos = maze.get_opposite_corner(new_x, new_y)
                if teleport_pos: new_state.position = teleport_pos

            # Collect food at new position
            if new_state.position in new_state.remaining_food:
                new_state.remaining_food.remove(new_state.position)

            # Handle magical pie effects
            if new_state.position in new_state.remaining_magical_pies:
                new_state.remaining_magical_pies.remove(new_state.position)
                new_state.walls_vanished_steps = 5  # Walls vanish for 5 steps

            successors.append(new_state)

        return successors