import sys
import time
from maze import Maze
from search import a_star_search, min_food_distance_heuristic, mst_heuristic
from visualization import Visualizer


def main():
    """Main entry point for the Pacman A* search program"""
    # Check command line arguments
    if len(sys.argv) != 2:
        print("Usage: python main.py <layout_file>")
        sys.exit(1)

    layout_file = sys.argv[1]

    # Load the maze
    print(f"Loading maze from {layout_file}...")
    try:
        maze = Maze(layout_file)
    except Exception as e:
        print(f"Error loading maze: {e}")
        sys.exit(1)

    # Display maze information
    print(f"Maze loaded successfully!")
    print(f"Dimensions: {maze.width}x{maze.height}")
    print(f"Starting position: {maze.pacman_start}")
    print(f"Food points: {len(maze.food_points)}")
    print(f"Magical pies: {len(maze.magical_pies)}")

    # Run A* search with minimum food distance heuristic (more efficient for this problem)
    print("\nRunning A* search...")
    start_time = time.time()
    actions, cost = a_star_search(maze, min_food_distance_heuristic)
    end_time = time.time()

    if actions:
        print(f"Solution found!")
        print(f"Number of actions: {len(actions)}")
        print(f"Total cost: {cost}")
        print(f"Search time: {end_time - start_time:.2f} seconds")
        print("\nList of actions:")
        for i, action in enumerate(actions):
            print(f"{i + 1}: {action}")

        # Visualize the solution
        print("\nStarting visualization...")
        visualizer = Visualizer(maze)
        visualizer.visualize_solution(actions)
    else:
        print("No solution found!")


if __name__ == "__main__":
    main()