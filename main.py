#!/usr/bin/env python3
"""
Main entry point for Pacman A* Search
Handles command line arguments and runs the simulation
"""

import argparse
import time
from maze import Maze
from pacman import PacmanSearchProblem
from search import AStarSearch, NullHeuristic, NearestFoodHeuristic, MSTHeuristic
from visualization import PacmanVisualizer


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Pacman A* Search')
    parser.add_argument('--layout', required=True, help='Path to layout file')
    parser.add_argument('--heuristic', default='manhattan',
                        choices=['null', 'manhattan', 'mst'],
                        help='Heuristic function to use')
    parser.add_argument('--visualize', action='store_true',
                        help='Visualize solution with pygame')
    return parser.parse_args()


def main():
    """Main function to run the Pacman A* simulation."""
    # Parse command line arguments
    args = parse_arguments()

    # Load maze from layout file
    maze = Maze(args.layout)
    print(f"Loaded maze with dimensions {maze.width}x{maze.height}")
    print(f"Pacman starts at {maze.pacman_start}")
    print(f"Found {len(maze.food_positions)} food points and {len(maze.magical_pie_positions)} magical pies")

    # Create search problem
    problem = PacmanSearchProblem(maze)

    # Select heuristic function
    heuristic_map = {
        'null': NullHeuristic(),
        'manhattan': NearestFoodHeuristic(),
        'mst': MSTHeuristic()
    }
    heuristic = heuristic_map[args.heuristic]
    print(f"Using {args.heuristic} heuristic")

    # Run A* search
    print("Running A* search...")
    start_time = time.time()
    astar = AStarSearch(problem, heuristic)
    path, actions, cost = astar.search()
    end_time = time.time()
    print(f"Search completed in {end_time - start_time:.2f} seconds")

    # Output solution
    print("\nSolution:")
    print(f"Actions: {actions}")
    print(f"Total cost: {cost}")
    print(f"States explored: {astar.nodes_expanded}")

    # Visualize if requested
    if args.visualize:
        print("\nStarting visualization. Press any key to begin animation.")
        visualizer = PacmanVisualizer(maze, path)
        visualizer.run()


if __name__ == "__main__":
    main()