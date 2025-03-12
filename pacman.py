class PacmanState:
    def __init__(self, position, remaining_food, remaining_magical_pies, wall_pass_steps=0, actions=None, cost=0):
        self.position = position  # (x, y)
        # Ensure these are sets for efficient membership testing and hashing
        self.remaining_food = set(remaining_food)  # Set of (x, y) coordinates
        self.remaining_magical_pies = set(remaining_magical_pies)  # Set of (x, y) coordinates
        self.wall_pass_steps = wall_pass_steps  # Number of steps Pacman can pass through walls (0-5)
        self.actions = actions if actions else []  # List of actions taken to reach this state
        self.cost = cost  # Total cost (number of steps)

    def __eq__(self, other):
        """Equality comparison for states"""
        if not isinstance(other, PacmanState):
            return False
        return (self.position == other.position and
                self.remaining_food == other.remaining_food and
                self.remaining_magical_pies == other.remaining_magical_pies and
                self.wall_pass_steps == other.wall_pass_steps)

    def __hash__(self):
        """Hash function for state to use in sets and dictionaries"""
        # Using frozenset to make the sets hashable
        return hash((self.position, frozenset(self.remaining_food),
                     frozenset(self.remaining_magical_pies), self.wall_pass_steps))

    def is_goal(self):
        """Check if this is a goal state (all food collected)"""
        return len(self.remaining_food) == 0

    def can_pass_walls(self):
        """Check if Pacman can pass through walls in this state"""
        return self.wall_pass_steps > 0

    def get_successor_states(self, maze):
        """Get all possible successor states from current state"""
        successor_states = []
        x, y = self.position

        # Get valid moves from the current position
        valid_moves = maze.get_valid_moves(x, y, self.can_pass_walls())

        for action, (new_x, new_y) in valid_moves:
            # Skip if trying to move into a wall without wall-pass ability
            if maze.is_wall(new_x, new_y) and not self.can_pass_walls():
                continue

            # Calculate new wall pass steps after this move
            new_wall_pass_steps = max(0, self.wall_pass_steps - 1) if action != 'Stop' else self.wall_pass_steps

            # Check if this move would leave Pacman stuck in a wall after wall-pass expires
            # If moving to a wall and this is the last wall-pass step, don't generate this state
            if maze.is_wall(new_x, new_y) and new_wall_pass_steps == 0:
                continue

            # Create a new state for each valid move
            new_state = PacmanState(
                position=(new_x, new_y),
                remaining_food=self.remaining_food.copy(),
                remaining_magical_pies=self.remaining_magical_pies.copy(),
                wall_pass_steps=new_wall_pass_steps,
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
                new_state.wall_pass_steps = 5  # Reset wall pass steps after eating pie

            successor_states.append(new_state)

        return successor_states