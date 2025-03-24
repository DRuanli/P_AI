class Maze:
    def __init__(self, file_path, logger=None):
        self.grid = []
        self.width = 0
        self.height = 0
        self.pacman_start = None
        self.food_points = []
        self.magical_pies = []
        self.logger = logger
        self.load_maze(file_path)

    def load_maze(self, file_path):
        """Load maze from a file and parse its contents"""
        if self.logger:
            self.logger.info(f"Loading maze from file: {file_path}")

        with open(file_path, 'r') as file:
            lines = file.readlines()

        for y, line in enumerate(lines):
            row = []
            for x, cell in enumerate(line.strip()):
                row.append(cell)
                if cell == 'P':
                    self.pacman_start = (x, y)
                    if self.logger:
                        self.logger.info(f"Pacman start position found at ({x}, {y})")
                elif cell == '.':
                    self.food_points.append((x, y))
                    if self.logger:
                        self.logger.debug(f"Food point found at ({x}, {y})")
                elif cell == 'O':
                    self.magical_pies.append((x, y))
                    if self.logger:
                        self.logger.debug(f"Magical pie found at ({x}, {y})")
            self.grid.append(row)

        self.height = len(self.grid)
        self.width = len(self.grid[0]) if self.height > 0 else 0

        if self.logger:
            self.logger.info(f"Maze loaded, dimensions: {self.width}x{self.height}")
            self.logger.info(f"Total food points: {len(self.food_points)}")
            self.logger.info(f"Total magical pies: {len(self.magical_pies)}")

    def is_wall(self, x, y):
        """Check if the given position is a wall"""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.grid[y][x] == '%'
        return True

    def is_corner(self, x, y):
        """Check if position is at a corner of the maze"""
        # Per the problem specification: corners are the extremes of the maze
        # Checking if the position is at the edge of the maze (not including walls)
        if self.is_wall(x, y):
            return False

        # Cache computation of corners for efficiency
        if not hasattr(self, '_corner_positions'):
            # Compute the corners once and cache them
            non_wall_positions = []
            for j in range(self.height):
                for i in range(self.width):
                    if not self.is_wall(i, j):
                        non_wall_positions.append((i, j))

            if not non_wall_positions:
                self._corner_positions = []
                return False

            min_x = min(pos[0] for pos in non_wall_positions)
            max_x = max(pos[0] for pos in non_wall_positions)
            min_y = min(pos[1] for pos in non_wall_positions)
            max_y = max(pos[1] for pos in non_wall_positions)

            # Store the four corner positions
            self._corner_positions = [
                (min_x, min_y),  # Top-left
                (min_x, max_y),  # Bottom-left
                (max_x, min_y),  # Top-right
                (max_x, max_y)  # Bottom-right
            ]

        # A corner is one of the four extreme points
        return (x, y) in self._corner_positions

    def get_opposite_corner(self, x, y):
        """Get the opposite corner of the maze"""
        if not self.is_corner(x, y):
            return None

        # Make sure corners are cached
        if not hasattr(self, '_corner_positions'):
            # This call will populate the _corner_positions cache
            self.is_corner(x, y)

        # Get index of the current corner
        try:
            idx = self._corner_positions.index((x, y))
        except ValueError:
            return None

        # Return the diagonally opposite corner
        # 0->3, 1->2, 2->1, 3->0
        opposite_idx = 3 - idx
        return self._corner_positions[opposite_idx]

    def get_valid_moves(self, x, y, walls_vanished):
        """Get valid moves from the current position"""
        valid_moves = []

        for direction, (dx, dy) in [('North', (0, -1)), ('East', (1, 0)),
                                    ('South', (0, 1)), ('West', (-1, 0))]:
            nx, ny = x + dx, y + dy

            # Check if position is within bounds
            if 0 <= nx < self.width and 0 <= ny < self.height:
                # If walls are vanished, we can go anywhere (except maze boundaries)
                if walls_vanished:
                    valid_moves.append((direction, (nx, ny)))
                # If walls are not vanished, we can only move to non-wall cells
                elif not self.is_wall(nx, ny):
                    valid_moves.append((direction, (nx, ny)))

        # Add 'Stop' action
        valid_moves.append(('Stop', (x, y)))

        return valid_moves