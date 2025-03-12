class PacmanState:
    def __init__(self, position, remaining_food, remaining_magical_pies, walls_vanished_steps=0, actions=None, cost=0):
        self.position = position  # (x, y)
        # Ensure these are sets for efficient membership testing and hashing
        self.remaining_food = set(remaining_food)  # Set of (x, y) coordinates
        self.remaining_magical_pies = set(remaining_magical_pies)  # Set of (x, y) coordinates
        self.walls_vanished_steps = walls_vanished_steps  # Number of steps walls remain vanished (0-5)
        self.actions = actions if actions else []  # List of actions taken to reach this state
        self.cost = cost  # Total cost (number of steps)

    def __eq__(self, other):
        """Equality comparison for states"""
        if not isinstance(other, PacmanState):
            return False
        return (self.position == other.position and
                self.remaining_food == other.remaining_food and
                self.remaining_magical_pies == other.remaining_magical_pies and
                self.walls_vanished_steps == other.walls_vanished_steps)

    def __hash__(self):
        """Hash function for state to use in sets and dictionaries"""
        # Using frozenset to make the sets hashable
        return hash((self.position, frozenset(self.remaining_food),
                     frozenset(self.remaining_magical_pies), self.walls_vanished_steps))

    def is_goal(self):
        """Check if this is a goal state (all food collected)"""
        return len(self.remaining_food) == 0

    def are_walls_vanished(self):
        """Check if walls are currently vanished"""
        return self.walls_vanished_steps > 0

    def get_successor_states(self, maze):
        """Get all possible successor states from current state"""
        successor_states = []
        x, y = self.position

        # Get valid moves from the current position
        valid_moves = maze.get_valid_moves(x, y, self.are_walls_vanished())

        for action, (new_x, new_y) in valid_moves:
            # Skip if trying to move into a wall when walls aren't vanished
            if maze.is_wall(new_x, new_y) and not self.are_walls_vanished():
                continue

            # Calculate new walls vanished steps after this move
            new_walls_vanished_steps = max(0,
                                           self.walls_vanished_steps - 1) if action != 'Stop' else self.walls_vanished_steps

            # Check if walls are about to reappear and would trap Pacman
            # If moving to a wall and this is the last step with vanished walls, don't generate this state
            if maze.is_wall(new_x, new_y) and new_walls_vanished_steps == 0:
                continue

            # Create a new state for each valid move
            new_state = PacmanState(
                position=(new_x, new_y),
                remaining_food=self.remaining_food.copy(),
                remaining_magical_pies=self.remaining_magical_pies.copy(),
                walls_vanished_steps=new_walls_vanished_steps,
                actions=self.actions + [action],
                cost=self.cost + 1 if action != 'Stop' else self.cost
            )

            # Check if the new position is a corner for teleportation
            if maze.is_corner(new_x, new_y):
                teleport_pos = maze.get_opposite_corner(new_x, new_y)
                if teleport_pos:
                    new_state.position = teleport_pos

            # Check if food at the new position
            if new_state.position in new_state.remaining_food:
                new_state.remaining_food.remove(new_state.position)

            # Check if magical pie at the new position
            if new_state.position in new_state.remaining_magical_pies:
                new_state.remaining_magical_pies.remove(new_state.position)
                new_state.walls_vanished_steps = 5  # Walls vanish for next 5 steps

            successor_states.append(new_state)

        return successor_states