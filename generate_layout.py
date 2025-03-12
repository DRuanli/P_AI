import argparse
import random
import os


def parse_args():
    """Parse command line arguments for maze generation."""
    parser = argparse.ArgumentParser(description='Generate a random Pacman maze layout')

    # Maze dimensions
    parser.add_argument('--width', type=int, default=30, help='Width of the maze (default: 30)')
    parser.add_argument('--height', type=int, default=15, help='Height of the maze (default: 15)')

    # Maze content
    parser.add_argument('--wall-density', type=float, default=0.3,
                        help='Probability of a cell being a wall (default: 0.3)')
    parser.add_argument('--food', type=int, default=5,
                        help='Number of food points (default: 5)')
    parser.add_argument('--magical-pies', type=int, default=3,
                        help='Number of magical pies (default: 3)')

    # Pacman starting position
    parser.add_argument('--pacman-x', type=int, default=None,
                        help='X coordinate for Pacman start (default: random)')
    parser.add_argument('--pacman-y', type=int, default=None,
                        help='Y coordinate for Pacman start (default: random)')

    # Output file
    parser.add_argument('--output', type=str, default='random_layout.txt',
                        help='Output file for the generated layout (default: random_layout.txt)')

    # Random seed for reproducibility
    parser.add_argument('--seed', type=int, default=None,
                        help='Random seed for reproducible layouts (default: random)')

    return parser.parse_args()


def generate_maze(args):
    """Generate a random maze based on the given parameters."""
    # Set random seed if specified
    if args.seed is not None:
        random.seed(args.seed)

    # Initialize empty maze
    maze = [['%' for _ in range(args.width)] for _ in range(args.height)]

    # Create border walls
    for y in range(args.height):
        for x in range(args.width):
            if x == 0 or x == args.width - 1 or y == 0 or y == args.height - 1:
                maze[y][x] = '%'  # Border walls
            else:
                # Randomly determine if this cell is a wall
                maze[y][x] = '%' if random.random() < args.wall_density else ' '

    # Find empty cells for placing entities
    empty_cells = []
    for y in range(1, args.height - 1):
        for x in range(1, args.width - 1):
            if maze[y][x] == ' ':
                empty_cells.append((x, y))

    # If no empty cells, create some
    if not empty_cells:
        center_x, center_y = args.width // 2, args.height // 2
        maze[center_y][center_x] = ' '
        empty_cells.append((center_x, center_y))

        # Create a small area around the center
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                nx, ny = center_x + dx, center_y + dy
                if 0 < nx < args.width - 1 and 0 < ny < args.height - 1:
                    maze[ny][nx] = ' '
                    empty_cells.append((nx, ny))

    # Ensure path connectivity using a random walk
    # This helps ensure the maze is solvable
    start_cell = random.choice(empty_cells)
    visited = {start_cell}
    stack = [start_cell]

    while len(visited) < len(empty_cells) and stack:
        x, y = stack[-1]
        neighbors = []
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if (nx, ny) in empty_cells and (nx, ny) not in visited:
                neighbors.append((nx, ny))

        if neighbors:
            next_cell = random.choice(neighbors)
            visited.add(next_cell)
            stack.append(next_cell)
        else:
            stack.pop()

    # Place Pacman
    if args.pacman_x is not None and args.pacman_y is not None:
        # Use specified position
        pacman_x, pacman_y = args.pacman_x, args.pacman_y
        if maze[pacman_y][pacman_x] == '%':
            maze[pacman_y][pacman_x] = ' '  # Ensure position is empty
        empty_cells = [(x, y) for x, y in empty_cells if (x, y) != (pacman_x, pacman_y)]
    else:
        # Choose random position
        if not empty_cells:
            raise ValueError("No empty cells available for Pacman")
        pacman_x, pacman_y = random.choice(empty_cells)
        empty_cells.remove((pacman_x, pacman_y))

    maze[pacman_y][pacman_x] = 'P'

    # Place food
    food_count = min(args.food, len(empty_cells))
    for _ in range(food_count):
        if not empty_cells:
            break
        x, y = random.choice(empty_cells)
        empty_cells.remove((x, y))
        maze[y][x] = '.'

    # Place magical pies
    pie_count = min(args.magical_pies, len(empty_cells))
    for _ in range(pie_count):
        if not empty_cells:
            break
        x, y = random.choice(empty_cells)
        empty_cells.remove((x, y))
        maze[y][x] = 'O'

    return maze


def save_maze(maze, filename):
    """Save the generated maze to a file."""
    with open(filename, 'w') as f:
        for row in maze:
            f.write(''.join(row) + '\n')
    return filename


def main():
    """Generate a random maze layout based on command-line arguments."""
    args = parse_args()

    print(f"Generating random maze ({args.width}x{args.height})...")
    print(f"- Food points: {args.food}")
    print(f"- Magical pies: {args.magical_pies}")

    try:
        maze = generate_maze(args)
        output_file = save_maze(maze, args.output)
        print(f"Maze successfully generated and saved to {output_file}")

        # Print maze preview
        print("\nMaze preview:")
        for row in maze:
            print(''.join(row))

        print(f"\nYou can now run: python main.py {output_file}")

    except Exception as e:
        print(f"Error generating maze: {e}")


if __name__ == "__main__":
    main()