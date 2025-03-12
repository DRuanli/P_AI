"""
Maze representation and parsing for Pacman A* Search
"""


class Maze:
    """
    Represents the maze structure with walls, food, pies, and teleportation corners.
    Provides methods for navigation and querying maze elements.
    """

    def __init__(self, layout_file):
        """
        Initialize maze from layout file

        Args:
            layout_file (str): Path to layout file
        """
        self.grid = []
        self.width = 0
        self.height = 0
        self.pacman_start = None
        self.food_positions = set()
        self.magical_pie_positions = set()
        self.corners = []
        self.parse_layout(layout_file)
        self.identify_corners()

    def parse_layout(self, layout_file):
        """
        Parse maze layout from file

        Args:
            layout_file (str): Path to layout file

        Layout symbols:
            % - obstacles/walls
            P - initial location of pacman
            . - food points
            O - magical pies
            (space) - blank cells
        """
        try:
            with open(layout_file, 'r') as f:
                lines = f.readlines()

            # Filter out any empty lines
            lines = [line.rstrip() for line in lines if line.strip()]

            # Determine maze dimensions
            self.height = len(lines)
            self.width = max(len(line) for line in lines)

            # Initialize grid with empty spaces
            self.grid = [[' ' for _ in range(self.width)] for _ in range(self.height)]

            # Parse grid elements
            for y, line in enumerate(lines):
                for x, char in enumerate(line):
                    # Add cell to grid
                    self.grid[y][x] = char

                    # Record special cells
                    if char == 'P':
                        self.pacman_start = (x, y)
                    elif char == '.':
                        self.food_positions.add((x, y))
                    elif char == 'O':
                        self.magical_pie_positions.add((x, y))

            if self.pacman_start is None:
                raise ValueError("No Pacman starting position (P) found in layout")

        except FileNotFoundError:
            raise FileNotFoundError(f"Layout file not found: {layout_file}")
        except Exception as e:
            raise Exception(f"Error parsing layout file: {e}")

    def identify_corners(self):
        """Identify the four corners of the maze for teleportation"""
        # The corners are defined as the extreme points of the maze that aren't walls
        potential_corners = [
            (0, 0),  # Top-left
            (self.width - 1, 0),  # Top-right
            (0, self.height - 1),  # Bottom-left
            (self.width - 1, self.height - 1)  # Bottom-right
        ]

        # Filter out corners that are walls
        self.corners = [(x, y) for x, y in potential_corners if not self.is_wall(x, y)]

    def is_wall(self, x, y):
        """
        Check if position contains a wall or is out of bounds

        Args:
            x (int): X coordinate
            y (int): Y coordinate

        Returns:
            bool: True if position is a wall, False otherwise
        """
        # Check bounds
        if not (0 <= x < self.width and 0 <= y < self.height):
            return True

        # Check if cell is a wall
        return self.grid[y][x] == '%'

    def get_teleport_destination(self, x, y):
        """
        If position is a corner, return the opposite corner

        Args:
            x (int): X coordinate
            y (int): Y coordinate

        Returns:
            tuple: (x, y) of destination if teleport, None otherwise
        """
        if len(self.corners) < 2:
            return None

        pos = (x, y)
        if pos in self.corners:
            # Find the opposite corner
            idx = self.corners.index(pos)
            opposite_idx = (idx + 2) % len(self.corners)
            return self.corners[opposite_idx]

        return None

    def get_legal_moves(self, x, y, can_pass_walls=False):
        """
        Get list of legal directions from current position

        Args:
            x (int): X coordinate
            y (int): Y coordinate
            can_pass_walls (bool): Whether Pacman can pass through walls

        Returns:
            list: Legal directions as tuples (dx, dy, action_name)
        """
        # All possible moves: (dx, dy, action_name)
        moves = [
            (0, -1, 'North'),
            (1, 0, 'East'),
            (0, 1, 'South'),
            (-1, 0, 'West'),
            (0, 0, 'Stop')
        ]

        # Filter legal moves
        legal_moves = []
        for dx, dy, action in moves:
            new_x, new_y = x + dx, y + dy

            # Stop is always allowed
            if dx == 0 and dy == 0:
                legal_moves.append((dx, dy, action))
                continue

            # Check if move is legal
            if not self.is_wall(new_x, new_y) or can_pass_walls:
                legal_moves.append((dx, dy, action))

        return legal_moves

    def has_food(self, x, y):
        """Check if position has food"""
        return (x, y) in self.food_positions

    def has_magical_pie(self, x, y):
        """Check if position has a magical pie"""
        return (x, y) in self.magical_pie_positions

    def __str__(self):
        """String representation of the maze"""
        return '\n'.join(''.join(row) for row in self.grid)