class Maze:
    def __init__(self, file_path):
        self.grid = []
        self.width = 0
        self.height = 0
        self.pacman_start = None
        self.food_points = []
        self.magical_pies = []
        self.load_maze(file_path)

    def load_maze(self, file_path):
        """Load maze from a file and parse its contents"""
        with open(file_path, 'r') as file:
            lines = file.readlines()

        for y, line in enumerate(lines):
            row = []
            for x, cell in enumerate(line.strip()):
                row.append(cell)
                if cell == 'P':
                    self.pacman_start = (x, y)
                elif cell == '.':
                    self.food_points.append((x, y))
                elif cell == 'O':
                    self.magical_pies.append((x, y))
            self.grid.append(row)

        self.height = len(self.grid)
        self.width = len(self.grid[0]) if self.height > 0 else 0

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

        # Define corners as the four extreme points of the maze
        # For simplicity, we'll consider the four corners of the playable area
        non_wall_positions = []
        for j in range(self.height):
            for i in range(self.width):
                if not self.is_wall(i, j):
                    non_wall_positions.append((i, j))

        if not non_wall_positions:
            return False

        min_x = min(pos[0] for pos in non_wall_positions)
        max_x = max(pos[0] for pos in non_wall_positions)
        min_y = min(pos[1] for pos in non_wall_positions)
        max_y = max(pos[1] for pos in non_wall_positions)

        # A corner is one of the four extreme points
        return (x == min_x and y == min_y) or \
            (x == min_x and y == max_y) or \
            (x == max_x and y == min_y) or \
            (x == max_x and y == max_y)

    def get_opposite_corner(self, x, y):
        """Get the opposite corner of the maze"""
        if not self.is_corner(x, y):
            return None

        # Find all corners in the maze
        corners = []
        non_wall_positions = []

        # First get all non-wall positions to find the extremes
        for j in range(self.height):
            for i in range(self.width):
                if not self.is_wall(i, j):
                    non_wall_positions.append((i, j))

        if not non_wall_positions:
            return None

        min_x = min(pos[0] for pos in non_wall_positions)
        max_x = max(pos[0] for pos in non_wall_positions)
        min_y = min(pos[1] for pos in non_wall_positions)
        max_y = max(pos[1] for pos in non_wall_positions)

        # Define the four corners
        top_left = (min_x, min_y)
        top_right = (max_x, min_y)
        bottom_left = (min_x, max_y)
        bottom_right = (max_x, max_y)

        # Get the diagonally opposite corner
        if (x, y) == top_left:
            return bottom_right
        elif (x, y) == top_right:
            return bottom_left
        elif (x, y) == bottom_left:
            return top_right
        elif (x, y) == bottom_right:
            return top_left

        return None

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