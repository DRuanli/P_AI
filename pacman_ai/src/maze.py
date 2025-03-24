class Maze:
    """
    Represents a Pacman maze with walls, food points, and magical pies.

    Handles maze parsing, wall detection, corner identification, and valid movement logic.
    """

    def __init__(self, file_path: str, logger=None):
        """
        Initialize maze from file and set up internal data structures.

        Args:
            file_path: Path to maze layout file
            logger: Optional logger for tracking operations
        """
        self.grid, self.width, self.height = [], 0, 0
        self.pacman_start, self.food_points, self.magical_pies = None, [], []
        self.logger = logger
        self.load_maze(file_path)

    def load_maze(self, file_path: str) -> None:
        """
        Load and parse maze layout file.

        Args:
            file_path: Path to maze text file where '%'=walls, 'P'=Pacman start,
                      '.'=food points, 'O'=magical pies
        """
        if self.logger: self.logger.info(f"Loading maze from file: {file_path}")

        with open(file_path, 'r') as file:
            lines = [line.strip() for line in file.readlines()]

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

        self.height, self.width = len(self.grid), len(self.grid[0]) if self.grid else 0

        if self.logger:
            self.logger.info(f"Maze loaded, dimensions: {self.width}x{self.height}")
            self.logger.info(f"Total food points: {len(self.food_points)}")
            self.logger.info(f"Total magical pies: {len(self.magical_pies)}")

    def is_wall(self, x: int, y: int) -> bool:
        """Check if position (x,y) is a wall"""
        return self.grid[y][x] == '%' if 0 <= x < self.width and 0 <= y < self.height else True

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

    def get_valid_moves(self, x: int, y: int, walls_vanished: bool) -> list:
        """
        Get valid moves from current position.

        Args:
            x, y: Current position coordinates
            walls_vanished: Whether walls are currently passable

        Returns:
            List of (direction, new_position) tuples
        """
        moves = []
        directions = [('North', (0, -1)), ('East', (1, 0)),
                      ('South', (0, 1)), ('West', (-1, 0))]

        for direction, (dx, dy) in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.width and 0 <= ny < self.height:
                if walls_vanished or not self.is_wall(nx, ny):
                    moves.append((direction, (nx, ny)))

        moves.append(('Stop', (x, y)))
        return moves