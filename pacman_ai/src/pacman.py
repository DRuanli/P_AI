class PacmanState:
    """
    Represents a state in the Pacman search problem, tracking position,
    remaining food/pies, wall status, and path information.
    """

    def __init__(self, position: tuple, remaining_food: set, remaining_magical_pies: set,
                 walls_vanished_steps: int = 0, actions: list = None, cost: int = 0,
                 ghost_positions: list = None, game_over: bool = False,
                 remaining_fruits: set = None, remaining_slow_pills: set = None,
                 remaining_speed_boosts: set = None, ghost_scared_steps: int = 0,
                 slow_motion_steps: int = 0, speed_boost_steps: int = 0,
                 moving_walls_active: bool = True):
        self.position = position  # (x, y) coordinates
        self.remaining_food = set(remaining_food)
        self.remaining_magical_pies = set(remaining_magical_pies)
        self.walls_vanished_steps = walls_vanished_steps  # Steps walls remain vanished (0-5)
        self.actions = actions or []  # Actions taken to reach this state
        self.cost = cost  # Total path cost (steps)
        self.ghost_positions = ghost_positions or []  # Positions of ghosts
        self.game_over = game_over  # Game over state (e.g., caught by ghost)

        # New mechanics
        self.remaining_fruits = set(remaining_fruits or [])  # Bonus fruits
        self.remaining_slow_pills = set(remaining_slow_pills or [])  # Slow motion power-ups
        self.remaining_speed_boosts = set(remaining_speed_boosts or [])  # Speed boost power-ups
        self.ghost_scared_steps = ghost_scared_steps  # Steps ghosts remain scared (0-20)
        self.slow_motion_steps = slow_motion_steps  # Steps ghosts move at half speed (0-15)
        self.speed_boost_steps = speed_boost_steps  # Steps Pacman moves twice per ghost move (0-10)
        self.moving_walls_active = moving_walls_active  # Whether moving walls are active

    def __eq__(self, other) -> bool:
        """Compare states based on position, remaining collectibles, and game status"""
        if not isinstance(other, PacmanState): return False
        return (self.position == other.position and
                self.remaining_food == other.remaining_food and
                self.remaining_magical_pies == other.remaining_magical_pies and
                self.walls_vanished_steps == other.walls_vanished_steps and
                self.ghost_positions == other.ghost_positions and
                self.game_over == other.game_over and
                self.remaining_fruits == other.remaining_fruits and
                self.remaining_slow_pills == other.remaining_slow_pills and
                self.remaining_speed_boosts == other.remaining_speed_boosts and
                self.ghost_scared_steps == other.ghost_scared_steps and
                self.slow_motion_steps == other.slow_motion_steps and
                self.speed_boost_steps == other.speed_boost_steps and
                self.moving_walls_active == other.moving_walls_active)

    def __hash__(self) -> int:
        """Hash function for use in sets and dictionaries"""
        return hash((self.position, frozenset(self.remaining_food),
                     frozenset(self.remaining_magical_pies), self.walls_vanished_steps,
                     tuple(self.ghost_positions), self.game_over,
                     frozenset(self.remaining_fruits), frozenset(self.remaining_slow_pills),
                     frozenset(self.remaining_speed_boosts), self.ghost_scared_steps,
                     self.slow_motion_steps, self.speed_boost_steps,
                     self.moving_walls_active))

    def is_goal(self) -> bool:
        """Check if all food has been collected and game is not over"""
        return not self.remaining_food and not self.game_over

    def are_ghosts_scared(self) -> bool:
        """Check if ghosts are currently scared (can be eaten by Pacman)"""
        return self.ghost_scared_steps > 0

    def is_slow_motion_active(self) -> bool:
        """Check if slow motion is active (ghosts move slower)"""
        return self.slow_motion_steps > 0

    def is_speed_boost_active(self) -> bool:
        """Check if speed boost is active (Pacman moves faster)"""
        return self.speed_boost_steps > 0

    def are_walls_vanished(self) -> bool:
        """Check if walls are currently passable"""
        return self.walls_vanished_steps > 0

    def move_ghosts(self, maze) -> list:
        """
        Move ghosts based on AI logic that depends on game state.
        When scared, ghosts flee from Pacman.
        When slow motion is active, ghosts have a chance to not move.

        Returns:
            List of new ghost positions
        """
        import random
        import math
        new_ghost_positions = []

        # Skip ghost movement if slow motion is active (50% chance each ghost doesn't move)
        if self.is_slow_motion_active() and random.random() < 0.5:
            return self.ghost_positions

        for ghost_pos in self.ghost_positions:
            x, y = ghost_pos
            valid_moves = []

            for dx, dy in [(0, -1), (1, 0), (0, 1), (-1, 0)]:  # North, East, South, West
                nx, ny = x + dx, y + dy
                if not maze.is_wall(nx, ny, self.moving_walls_active):
                    valid_moves.append(((nx, ny), (dx, dy)))

            if not valid_moves:
                new_ghost_positions.append(ghost_pos)  # Stay in place if no valid moves
                continue

            # If ghosts are scared, try to move away from Pacman
            if self.are_ghosts_scared():
                # Calculate distances to Pacman for each move
                distances = []
                for (nx, ny), _ in valid_moves:
                    # Manhattan distance to Pacman
                    dist = abs(nx - self.position[0]) + abs(ny - self.position[1])
                    distances.append(dist)

                # Find the moves with maximum distance (furthest from Pacman)
                max_dist = max(distances)
                best_moves = [move for move, dist in zip(valid_moves, distances) if dist == max_dist]

                # Choose randomly from best moves
                if best_moves:
                    chosen_move = random.choice(best_moves)[0]
                else:
                    chosen_move = random.choice([m[0] for m in valid_moves])

                new_ghost_positions.append(chosen_move)
            else:
                # Normal movement - random or with some tracking of Pacman
                new_ghost_positions.append(random.choice([m[0] for m in valid_moves]))

        return new_ghost_positions

    def check_ghost_collision(self) -> (bool, list):
        """
        Check if Pacman collides with any ghost

        Returns:
            (collision_occurred, eaten_ghosts): Tuple with collision status and list of eaten ghost indices
        """
        if not self.position in self.ghost_positions:
            return False, []

        # If ghosts are scared, Pacman eats them instead of dying
        if self.are_ghosts_scared():
            eaten_ghosts = [i for i, pos in enumerate(self.ghost_positions)
                            if pos == self.position]
            return True, eaten_ghosts

        # Otherwise, collision is fatal
        return True, []

    def get_successor_states(self, maze) -> list:
        """
        Generate all valid successor states from current position.

        Applies movement rules, teleportation, food collection,
        and various power-up effects.

        Params:
            maze: Maze object containing layout and movement rules

        Returns:
            List of valid PacmanState successors
        """
        successors = []

        # If game is over, no valid successors
        if self.game_over:
            return []

        x, y = self.position

        # Update power-up status timers
        new_scared_steps = max(0, self.ghost_scared_steps - 1)
        new_slow_steps = max(0, self.slow_motion_steps - 1)
        new_speed_steps = max(0, self.speed_boost_steps - 1)
        new_vanish_steps = max(0, self.walls_vanished_steps - 1)

        # Get valid moves considering current wall state
        valid_moves = maze.get_valid_moves(x, y, self.are_walls_vanished(), self.moving_walls_active)

        for action, (new_x, new_y) in valid_moves:
            # Skip invalid wall movements
            if maze.is_wall(new_x, new_y, self.moving_walls_active) and not self.are_walls_vanished():
                continue

            # Prevent getting trapped in walls
            if maze.is_wall(new_x, new_y, self.moving_walls_active) and new_vanish_steps == 0:
                continue

            # Move ghosts before creating new state (or not, if it's a "Stop" action)
            new_ghost_positions = self.ghost_positions
            if action != 'Stop':
                new_ghost_positions = self.move_ghosts(maze)

            # Create successor state with all current power-ups
            new_state = PacmanState(
                position=(new_x, new_y),
                remaining_food=self.remaining_food.copy(),
                remaining_magical_pies=self.remaining_magical_pies.copy(),
                walls_vanished_steps=new_vanish_steps if action != 'Stop' else self.walls_vanished_steps,
                actions=self.actions + [action],
                cost=self.cost + (0 if action == 'Stop' else 1),
                ghost_positions=new_ghost_positions,
                remaining_fruits=self.remaining_fruits.copy(),
                remaining_slow_pills=self.remaining_slow_pills.copy(),
                remaining_speed_boosts=self.remaining_speed_boosts.copy(),
                ghost_scared_steps=new_scared_steps if action != 'Stop' else self.ghost_scared_steps,
                slow_motion_steps=new_slow_steps if action != 'Stop' else self.slow_motion_steps,
                speed_boost_steps=new_speed_steps if action != 'Stop' else self.speed_boost_steps,
                moving_walls_active=self.moving_walls_active
            )

            # Handle corner teleportation
            if maze.is_corner(new_x, new_y):
                teleport_pos = maze.get_opposite_corner(new_x, new_y)
                if teleport_pos:
                    new_state.position = teleport_pos

            # Handle teleport pads
            teleport_dest = maze.check_teleport_pad(new_x, new_y)
            if teleport_dest:
                new_state.position = teleport_dest

            # Collect food at new position
            if new_state.position in new_state.remaining_food:
                new_state.remaining_food.remove(new_state.position)

            # Handle magical pie effects (activate scared ghosts + wall vanishing)
            if new_state.position in new_state.remaining_magical_pies:
                new_state.remaining_magical_pies.remove(new_state.position)
                new_state.walls_vanished_steps = 5  # Walls vanish for 5 steps
                new_state.ghost_scared_steps = 15  # Ghosts are scared for 15 steps

            # Handle fruit collection
            if new_state.position in new_state.remaining_fruits:
                new_state.remaining_fruits.remove(new_state.position)
                # Fruits could have various effects, random for now

            # Handle slow pill collection
            if new_state.position in new_state.remaining_slow_pills:
                new_state.remaining_slow_pills.remove(new_state.position)
                new_state.slow_motion_steps = 15  # Slow motion active for 15 steps

            # Handle speed boost collection
            if new_state.position in new_state.remaining_speed_boosts:
                new_state.remaining_speed_boosts.remove(new_state.position)
                new_state.speed_boost_steps = 10  # Speed boost active for 10 steps

            # Check ghost collision
            collision, eaten_ghosts = new_state.check_ghost_collision()
            if collision:
                if eaten_ghosts:  # Pacman ate some ghosts
                    # Remove eaten ghosts
                    for idx in sorted(eaten_ghosts, reverse=True):
                        if idx < len(new_state.ghost_positions):
                            new_state.ghost_positions.pop(idx)
                else:  # Pacman was caught
                    new_state.game_over = True

            # Toggle moving walls occasionally (every 10 steps)
            if self.cost > 0 and self.cost % 10 == 0 and action != 'Stop':
                new_state.moving_walls_active = not new_state.moving_walls_active

            successors.append(new_state)

        return successors