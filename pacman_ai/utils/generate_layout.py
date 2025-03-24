import random
import os
from collections import deque


class LayoutGenerator:
    """Generates random, playable layouts for Pacman A* search."""

    def __init__(self, width=25, height=15, food_density=0.15, magical_pie_density=0.05):
        """
        Initialize the layout generator with configurable parameters.

        Args:
            width: Width of the maze
            height: Height of the maze
            food_density: Percentage of open spaces with food (0.0-1.0)
            magical_pie_density: Percentage of open spaces with magical pies (0.0-1.0)
        """
        self.width = width
        self.height = height
        self.food_density = food_density
        self.magical_pie_density = magical_pie_density
        self.layout = []
        self.pacman_pos = None

    def generate_layout(self):
        """Generate a random, playable layout."""
        # Initialize layout with walls
        self.layout = [['%' for _ in range(self.width)] for _ in range(self.height)]

        # Create outer walls
        for y in range(self.height):
            for x in range(self.width):
                if y == 0 or y == self.height - 1 or x == 0 or x == self.width - 1:
                    self.layout[y][x] = '%'

        # Generate maze paths using a version of randomized Prim's algorithm
        self._generate_maze_paths()

        # Place Pacman
        self._place_pacman()

        # Ensure layout is connected (all open spaces reachable from Pacman)
        self._ensure_connected()

        # Place food and magical pies
        self._place_food_and_pies()

        return self.layout

    def _generate_maze_paths(self):
        """Generate pathways using a modified randomized Prim's algorithm."""
        # Start with a grid full of walls
        start_x, start_y = 2 * random.randint(1, (self.width - 2) // 2), 2 * random.randint(1, (self.height - 2) // 2)
        self.layout[start_y][start_x] = ' '  # Start with a single open cell

        # Add walls around the starting point to the wall list
        walls = []
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            nx, ny = start_x + dx, start_y + dy
            if 0 < nx < self.width - 1 and 0 < ny < self.height - 1:
                walls.append((nx, ny, start_x, start_y))

        # Process walls until none remain
        while walls:
            # Pick a random wall
            wall_idx = random.randint(0, len(walls) - 1)
            x, y, px, py = walls.pop(wall_idx)

            # Calculate the cell on the opposite side of the wall
            dx, dy = x - px, y - py
            nx, ny = x + dx, y + dy

            # If the opposite cell is a wall, create a passage
            if 0 < nx < self.width - 1 and 0 < ny < self.height - 1 and self.layout[ny][nx] == '%':
                self.layout[y][x] = ' '  # Make the wall a passage
                self.layout[ny][nx] = ' '  # Make the cell beyond a passage

                # Add new walls to the list
                for d_dx, d_dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                    new_x, new_y = nx + d_dx, ny + d_dy
                    if 0 < new_x < self.width - 1 and 0 < new_y < self.height - 1 and self.layout[new_y][new_x] == '%':
                        walls.append((new_x, new_y, nx, ny))

        # Add some random openings for more varied paths (optional)
        for _ in range((self.width * self.height) // 20):  # Adjust density as needed
            x, y = random.randint(1, self.width - 2), random.randint(1, self.height - 2)
            if self.layout[y][x] == '%':
                # Only create opening if it won't break outer wall
                if not (x == 0 or x == self.width - 1 or y == 0 or y == self.height - 1):
                    self.layout[y][x] = ' '

    def _place_pacman(self):
        """Place Pacman at a random open position."""
        open_positions = []
        for y in range(self.height):
            for x in range(self.width):
                if self.layout[y][x] == ' ':
                    open_positions.append((x, y))

        if open_positions:
            self.pacman_pos = random.choice(open_positions)
            x, y = self.pacman_pos
            self.layout[y][x] = 'P'

    def _ensure_connected(self):
        """Ensure all open spaces are reachable from Pacman."""
        if not self.pacman_pos:
            return

        # Use BFS to find all reachable cells
        visited = set()
        queue = deque([self.pacman_pos])
        visited.add(self.pacman_pos)

        while queue:
            x, y = queue.popleft()
            for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                nx, ny = x + dx, y + dy
                if (0 <= nx < self.width and 0 <= ny < self.height and
                        self.layout[ny][nx] != '%' and (nx, ny) not in visited):
                    visited.add((nx, ny))
                    queue.append((nx, ny))

        # Identify all open spaces
        all_open = set()
        for y in range(self.height):
            for x in range(self.width):
                if self.layout[y][x] != '%':
                    all_open.add((x, y))

        # Find unreachable spaces
        unreachable = all_open - visited

        # Connect unreachable spaces by removing walls
        for x, y in unreachable:
            # Try to connect to a reachable space
            connected = False
            neighbors = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
            random.shuffle(neighbors)

            for nx, ny in neighbors:
                if (nx, ny) in visited:
                    # Create a path
                    wall_x, wall_y = (x + nx) // 2, (y + ny) // 2
                    if 0 <= wall_x < self.width and 0 <= wall_y < self.height:
                        self.layout[wall_y][wall_x] = ' '
                        connected = True
                        break

            if not connected and self.layout[y][x] != 'P':
                # If can't connect, turn into a wall (except Pacman)
                self.layout[y][x] = '%'

    def _place_food_and_pies(self):
        """Place food dots and magical pies in the maze."""
        open_positions = []
        for y in range(self.height):
            for x in range(self.width):
                if self.layout[y][x] == ' ':  # Only on empty spaces
                    open_positions.append((x, y))

        # Shuffle positions for random placement
        random.shuffle(open_positions)

        # Calculate number of food dots and magical pies
        num_food = int(len(open_positions) * self.food_density)
        num_pies = min(int(len(open_positions) * self.magical_pie_density), len(open_positions) - num_food)

        # Place food dots
        for i in range(num_food):
            if i < len(open_positions):
                x, y = open_positions[i]
                self.layout[y][x] = '.'

        # Place magical pies
        for i in range(num_food, num_food + num_pies):
            if i < len(open_positions):
                x, y = open_positions[i]
                self.layout[y][x] = 'O'

    def save_layout(self, filename):
        """Save the generated layout to a file."""
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w') as f:
            for row in self.layout:
                f.write(''.join(row) + '\n')
        return filename

    def to_string(self):
        """Convert layout to a string."""
        return '\n'.join([''.join(row) for row in self.layout])


def generate_random_layout(width=30, height=15, food_density=0.15,
                           magical_pie_density=0.05, filename=None):
    """
    Generate a random playable layout and optionally save to file.

    Args:
        width: Width of the maze
        height: Height of the maze
        food_density: Percentage of open spaces with food (0.0-1.0)
        magical_pie_density: Percentage of open spaces with magical pies (0.0-1.0)
        filename: Optional filename to save layout

    Returns:
        If filename provided: Path to saved layout file
        Otherwise: Layout as a string
    """
    generator = LayoutGenerator(width, height, food_density, magical_pie_density)
    generator.generate_layout()

    if filename:
        return generator.save_layout(filename)
    else:
        return generator.to_string()


# Example usage
if __name__ == "__main__":
    # Generate and print a random layout
    layout = generate_random_layout()
    print(layout)

    # Generate and save a layout to file
    filename = "layouts/random_layout.txt"
    generate_random_layout(filename=filename)
    print(f"Layout saved to {filename}")