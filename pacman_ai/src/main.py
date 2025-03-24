import sys
import time
import argparse
import logging
from datetime import datetime
from maze import Maze
from search import a_star_search, min_food_distance_heuristic, mst_heuristic
from visualization import Visualizer


def setup_logger():
    """Set up the logger to track execution history."""
    # Create logger
    logger = logging.getLogger('pacman_a_star')
    logger.setLevel(logging.INFO)

    # Create file handler
    file_handler = logging.FileHandler('logs/history.txt')
    file_handler.setLevel(logging.INFO)

    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)  # Only warnings and errors to console

    # Create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Add the handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


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
    # Set up logger
    logger = setup_logger()
    logger.info("------------------------------------")
    logger.info("------------------------------------")
    logger.info("----- New Pacman A* Search Run -----")
    logger.info(f"Start time: {datetime.now()}")

    # Parse command line arguments
    args = parse_args()
    logger.info(f"Arguments: {args}")

    # Load the maze
    print(f"Loading maze from {args.layout_file}...")
    logger.info(f"Loading maze from {args.layout_file}")
    try:
        maze = Maze(args.layout_file, logger)
        logger.info(f"Maze loaded successfully")
    except Exception as e:
        error_msg = f"Error loading maze: {e}"
        print(error_msg)
        logger.error(error_msg)
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
        logger.info("Using Minimum Food Distance heuristic")
    else:
        heuristic = mst_heuristic
        print("\nRunning A* search with Minimum Spanning Tree heuristic...")
        logger.info("Using Minimum Spanning Tree heuristic")

    # Run A* search
    logger.info("Starting A* search")
    start_time = time.time()
    actions, cost = a_star_search(maze, heuristic, logger)
    end_time = time.time()
    search_time = end_time - start_time
    logger.info(f"A* search completed in {search_time:.2f} seconds")

    if actions:
        print(f"Solution found!")
        print(f"Number of actions: {len(actions)}")
        print(f"Total cost: {cost}")
        print(f"Search time: {search_time:.2f} seconds")

        logger.info(f"Solution found with {len(actions)} actions and cost {cost}")

        # Log the solution
        logger.info("Solution actions:")
        for i, action in enumerate(actions):
            logger.info(f"  {i + 1}: {action}")

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
                logger.info(f"Solution saved to {args.output}")
            except Exception as e:
                error_msg = f"Error saving solution: {e}"
                print(error_msg)
                logger.error(error_msg)

        # Visualize the solution if not disabled
        if not args.no_visual:
            print("\nStarting visualization...")
            logger.info("Starting visualization")
            visualizer = Visualizer(maze, cell_size=args.cell_size, step_delay=args.delay, logger=logger)
            visualizer.visualize_solution(actions)
            logger.info("Visualization completed")
        else:
            print("\nVisualization skipped.")
            logger.info("Visualization skipped")
    else:
        print("No solution found!")
        logger.warning("No solution found!")

    logger.info(f"Run completed at {datetime.now()}")
    logger.info("----- End of Run -----\n")
    logger.info("----------------------")
    logger.info("----------------------")


if __name__ == "__main__":
    main()