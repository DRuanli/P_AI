class Maze:
    """
    Represents a Pacman maze with walls, food points, and magical pies.

    Handles maze parsing, wall detection, corner identification, and valid movement logic.
    """

    def __init__(self, file_path: str, logger=None):
        self.grid, self.width, self.height = [], 0, 0
        self.pacman_start, self.food_points, self.magical_pies = None, [], []
        self.ghost_starts = []  # Add ghost starting positions
        self.fruit_spawn_points = []  # Fruit bonus spawn points
        self.teleport_pads = {}  # Teleport pad positions and their connections
        self.moving_walls = []  # Moving wall positions and states
        self.slow_pills = []  # Time slowdown power-ups
        self.speed_boosts = []  # Speed boost power-ups
        self.logger = logger
        self.load_maze(file_path)

    def load_maze(self, file_path: str) -> None:
        """
        Load and parse maze layout file.

        Params:
            file_path: Path to maze text file where:
                '%'=walls, 'P'=Pacman start, '.'=food points, 'O'=magical pies,
                'G'=ghost start, 'F'=fruit spawn, 'T'=teleport pad, 'M'=moving wall,
                'S'=slow pill, 'B'=speed boost
        """
        if self.logger: self.logger.info(f"Loading maze from file: {file_path}")

        with open(file_path, 'r') as file:
            lines = [line.strip() for line in file.readlines()]

        teleport_pad_ids = {}  # To track teleport pad IDs
        teleport_count = 0  # Counter for pad pairs

        for y, line in enumerate(lines):
            self.grid.append(list(line))
            for x, cell in enumerate(line):
                if cell == 'P':
                    self.pacman_start = (x, y)
                    if self.logger: self.logger.info(f"Pacman start position found at ({x}, {y})")
                elif cell == '.':
                    self.food_points.append((x, y))
                elif cell == 'O':
                    self.magical_pies.append((x, y))
                elif cell == 'G':  # Ghost start positions
                    self.ghost_starts.append((x, y))
                    if self.logger: self.logger.info(f"Ghost start position found at ({x}, {y})")
                elif cell == 'F':  # Fruit spawn point
                    self.fruit_spawn_points.append((x, y))
                    if self.logger: self.logger.info(f"Fruit spawn point found at ({x}, {y})")
                elif cell == 'T':  # Teleport pad
                    # Assign teleport pads in pairs
                    pad_id = teleport_count // 2
                    if pad_id not in teleport_pad_ids:
                        teleport_pad_ids[pad_id] = [(x, y)]
                    else:
                        teleport_pad_ids[pad_id].append((x, y))
                        # Connect both pads
                        self.teleport_pads[teleport_pad_ids[pad_id][0]] = teleport_pad_ids[pad_id][1]
                        self.teleport_pads[teleport_pad_ids[pad_id][1]] = teleport_pad_ids[pad_id][0]
                    teleport_count += 1
                    if self.logger: self.logger.info(f"Teleport pad found at ({x}, {y}), ID: {pad_id}")
                elif cell == 'M':  # Moving wall
                    self.moving_walls.append((x, y))
                    if self.logger: self.logger.info(f"Moving wall found at ({x}, {y})")
                elif cell == 'S':  # Slow pill
                    self.slow_pills.append((x, y))
                    if self.logger: self.logger.info(f"Slow pill found at ({x}, {y})")
                elif cell == 'B':  # Speed boost
                    self.speed_boosts.append((x, y))
                    if self.logger: self.logger.info(f"Speed boost found at ({x}, {y})")

        # Add default ghost positions if fewer than 2 were found
        self.height, self.width = len(self.grid), len(self.grid[0]) if self.grid else 0
        while len(self.ghost_starts) < 2:
            # Find valid position for ghost (not a wall, not pacman start)
            for y in range(self.height):
                for x in range(self.width):
                    if not self.is_wall(x, y) and (x, y) != self.pacman_start and (x, y) not in self.ghost_starts:
                        self.ghost_starts.append((x, y))
                        if self.logger: self.logger.info(f"Default ghost position added at ({x}, {y})")
                        break
                if len(self.ghost_starts) >= 2:
                    break

        # Add default teleport pads if none were found
        if not self.teleport_pads and self.height > 5 and self.width > 5:
            default_pads = []
            # Find valid positions for teleport pads
            for y in range(self.height):
                for x in range(self.width):
                    if not self.is_wall(x, y) and (x, y) != self.pacman_start and (
                    x, y) not in self.ghost_starts and len(default_pads) < 2:
                        default_pads.append((x, y))
                        if self.logger: self.logger.info(f"Default teleport pad added at ({x}, {y})")

            if len(default_pads) == 2:
                self.teleport_pads[default_pads[0]] = default_pads[1]
                self.teleport_pads[default_pads[1]] = default_pads[0]

        # Add default slow pills and speed boosts if none were found
        if not self.slow_pills and self.height > 3 and self.width > 3:
            for y in range(self.height):
                for x in range(self.width):
                    if not self.is_wall(x, y) and (x, y) != self.pacman_start and (x, y) not in self.ghost_starts and (
                    x, y) not in self.slow_pills:
                        self.slow_pills.append((x, y))
                        if self.logger: self.logger.info(f"Default slow pill added at ({x}, {y})")
                        break
                if self.slow_pills:
                    break

        if not self.speed_boosts and self.height > 3 and self.width > 3:
            for y in range(self.height):
                for x in range(self.width):
                    if not self.is_wall(x, y) and (x, y) != self.pacman_start and (x, y) not in self.ghost_starts and (
                    x, y) not in self.slow_pills and (x, y) not in self.speed_boosts:
                        self.speed_boosts.append((x, y))
                        if self.logger: self.logger.info(f"Default speed boost added at ({x}, {y})")
                        break
                if self.speed_boosts:
                    break

        if self.logger:
            self.logger.info(f"Maze loaded, dimensions: {self.width}x{self.height}")
            self.logger.info(f"Total food points: {len(self.food_points)}")
            self.logger.info(f"Total magical pies: {len(self.magical_pies)}")
            self.logger.info(f"Total ghosts: {len(self.ghost_starts)}")
            self.logger.info(f"Total teleport pads: {len(self.teleport_pads) // 2}")
            self.logger.info(f"Total slow pills: {len(self.slow_pills)}")
            self.logger.info(f"Total speed boosts: {len(self.speed_boosts)}")
            self.logger.info(f"Total fruit spawn points: {len(self.fruit_spawn_points)}")
            self.logger.info(f"Total moving walls: {len(self.moving_walls)}")

    def is_wall(self, x: int, y: int, moving_walls_active=True) -> bool:
        """
        Check if position (x,y) is a wall

        Params:
            x, y: Coordinates to check
            moving_walls_active: Whether moving walls should be active
        """
        if not (0 <= x < self.width and 0 <= y < self.height):
            return True

        # Check normal walls
        if self.grid[y][x] == '%':
            return True

        # Check moving walls when active
        if moving_walls_active and (x, y) in self.moving_walls:
            return True

        return False

    def check_teleport_pad(self, x: int, y: int) -> tuple:
        """Check if position is a teleport pad and return connected pad position"""
        pos = (x, y)
        return self.teleport_pads.get(pos, None)

    def is_corner(self, x: int, y: int) -> bool:
        """Determine if position is at one of the four extreme corners of non-wall area"""
        if self.is_wall(x, y): return False

        # Compute and cache corners if not already done
        if not hasattr(self, '_corner_positions'):
            non_wall_positions = [(i, j) for j in range(self.height)
                                  for i in range(self.width) if not self.is_wall(i, j)]

            if not non_wall_positions:
                self._corner_positions = []
                return False

            x_vals, y_vals = zip(*non_wall_positions)
            min_x, max_x, min_y, max_y = min(x_vals), max(x_vals), min(y_vals), max(y_vals)

            self._corner_positions = [
                (min_x, min_y), (min_x, max_y),  # Left corners
                (max_x, min_y), (max_x, max_y)  # Right corners
            ]

        return (x, y) in self._corner_positions

    def get_opposite_corner(self, x: int, y: int) -> tuple:
        """Get diagonal opposite corner coordinates or None if not a corner"""
        if not self.is_corner(x, y): return None

        # Ensure corners are cached
        if not hasattr(self, '_corner_positions'):
            self.is_corner(x, y)

        try:
            idx = self._corner_positions.index((x, y))
            return self._corner_positions[3 - idx]  # Opposite corner index pattern: 0↔3, 1↔2
        except ValueError:
            return None

    def get_valid_moves(self, x: int, y: int, walls_vanished: bool, moving_walls_active=True) -> list:
        """
        Get valid moves from current position.

        Params:
            x, y: Current position coordinates
            walls_vanished: Whether walls are currently passable
            moving_walls_active: Whether moving walls should block movement

        Returns:
            List of (direction, new_position) tuples
        """
        moves = []
        directions = [('North', (0, -1)), ('East', (1, 0)),
                      ('South', (0, 1)), ('West', (-1, 0))]

        for direction, (dx, dy) in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.width and 0 <= ny < self.height:
                if walls_vanished or not self.is_wall(nx, ny, moving_walls_active):
                    moves.append((direction, (nx, ny)))

        moves.append(('Stop', (x, y)))
        return moves

    def spawn_fruit(self) -> tuple:
        """
        Spawns a fruit at a random spawn point

        Returns:
            Coordinates of the spawned fruit, or None if no spawn points
        """
        import random
        if self.fruit_spawn_points:
            return random.choice(self.fruit_spawn_points)
        return None

    def toggle_moving_walls(self) -> None:
        """Toggle state of moving walls (open/close)"""
        # This would actually modify the grid in a real implementation
        pass