import sys
import time
import argparse
from maze import Maze
from search import a_star_search, min_food_distance_heuristic, mst_heuristic
from visualization import Visualizer


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Pacman A* Search Implementation')

    # Required argument: layout file
    parser.add_argument('layout_file', type=str, help='Path to the layout file')

    # Optional arguments
    parser.add_argument('--heuristic', type=str, choices=['mfd', 'mst'], default='mfd',
                        help='Heuristic to use: min_food_distance (mfd) or minimum_spanning_tree (mst)')

    parser.add_argument('--no-visual', action='store_true', default=False,
                        help='Skip visualization and only print the solution')

    parser.add_argument('--cell-size', type=int, default=20,
                        help='Cell size for visualization (default: 20 pixels)')

    parser.add_argument('--delay', type=float, default=0.3,
                        help='Delay between steps in visualization (default: 0.3 seconds)')

    parser.add_argument('--output', type=str, default=None,
                        help='Output file to write the solution (optional)')

    return parser.parse_args()


def main():
    """Main entry point for the Pacman A* search program"""
    # Parse command line arguments
    args = parse_args()

    # Load the maze
    print(f"Loading maze from {args.layout_file}...")
    try:
        maze = Maze(args.layout_file)
    except Exception as e:
        print(f"Error loading maze: {e}")
        sys.exit(1)

    # Display maze information
    print(f"Maze loaded successfully!")
    print(f"Dimensions: {maze.width}x{maze.height}")
    print(f"Starting position: {maze.pacman_start}")
    print(f"Food points: {len(maze.food_points)}")
    print(f"Magical pies: {len(maze.magical_pies)}")

    # Select heuristic
    if args.heuristic == 'mfd':
        heuristic = min_food_distance_heuristic
        print("\nRunning A* search with Minimum Food Distance heuristic...")
    else:
        heuristic = mst_heuristic
        print("\nRunning A* search with Minimum Spanning Tree heuristic...")

    # Run A* search
    start_time = time.time()
    actions, cost = a_star_search(maze, heuristic)
    end_time = time.time()

    if actions:
        print(f"Solution found!")
        print(f"Number of actions: {len(actions)}")
        print(f"Total cost: {cost}")
        print(f"Search time: {end_time - start_time:.2f} seconds")

        # Print or save the solution
        print("\nList of actions:")
        for i, action in enumerate(actions):
            print(f"{i + 1}: {action}")

        # Save to output file if specified
        if args.output:
            try:
                with open(args.output, 'w') as f:
                    f.write(f"Total cost: {cost}\n")
                    f.write("Actions:\n")
                    for action in actions:
                        f.write(f"{action}\n")
                print(f"\nSolution saved to {args.output}")
            except Exception as e:
                print(f"Error saving solution: {e}")

        # Visualize the solution if not disabled
        if not args.no_visual:
            print("\nStarting visualization...")
            visualizer = Visualizer(maze, cell_size=args.cell_size, step_delay=args.delay)
            visualizer.visualize_solution(actions)
        else:
            print("\nVisualization skipped.")
    else:
        print("No solution found!")


if __name__ == "__main__":
    main()