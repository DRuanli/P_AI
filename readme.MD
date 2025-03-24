# Pacman A* Pathfinding AI

## Overview

This project implements an A* search algorithm to find optimal paths for Pacman to collect all food dots in various maze layouts. The implementation includes advanced features such as:

- Optimal pathfinding with admissible heuristics
- Magical pies that allow Pacman to pass through walls temporarily
- Teleportation between corner points
- Interactive visualization of the solution
- Customizable maze layouts

## Requirements

- Python 3.9+
- Pygame (for visualization)
- Additional libraries: None required beyond Python standard library

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/DRuanli/Pacman_AI.git
   cd Pacman_AI
   ```

2. Create a virtual environment (optional but recommended):
   ```
   python -m venv .venv
   source .venv/bin/activate  # On Windows, use: .venv\Scripts\activate
   ```

3. Install required packages:
   ```
   pip install pygame
   ```

## Project Structure

```
pacman_ai/
├── layouts/                # Maze layout files
│   ├── example_layout.txt  # Simple example layout
│   ├── smallMaze.txt       # Small maze for testing
│   ├── mediumMaze.txt      # Medium-sized maze
│   └── random_layout.txt   # Randomly generated layout
├── logs/                   # Execution history logs
│   └── history.txt
├── src/                    # Source code
│   ├── main.py             # Entry point and argument handling
│   ├── maze.py             # Maze representation and movement logic
│   ├── pacman.py           # Pacman state representation
│   ├── search.py           # A* search implementation with heuristics
│   └── visualization.py    # Pygame-based solution visualization
└── utils/                  # Utility scripts
    └── generate_layout.py  # Random layout generator
```

## Usage

### Basic Usage

Run the program with a layout file:

```
python pacman_ai/src/main.py pacman_ai/layouts/smallMaze.txt
```

### Command-line Arguments

- `layout_file`: Path to the layout file (required)
- `--heuristic`: Heuristic to use: `mfd` (minimum food distance) or `mst` (minimum spanning tree, default)
- `--no-visual`: Skip visualization and only print the solution
- `--cell-size`: Cell size for visualization (default: 30 pixels)
- `--delay`: Delay between steps in visualization (default: 0.3 seconds)
- `--output`: Output file to write the solution (optional)

### Examples

Run with minimum spanning tree heuristic (default):
```
python pacman_ai/src/main.py pacman_ai/layouts/mediumMaze.txt
```

Run with minimum food distance heuristic:
```
python pacman_ai/src/main.py pacman_ai/layouts/smallMaze.txt --heuristic mfd
```

Increase visualization cell size and slow down animation:
```
python pacman_ai/src/main.py pacman_ai/layouts/example_layout.txt --cell-size 40 --delay 0.5
```

Run without visualization:
```
python pacman_ai/src/main.py pacman_ai/layouts/random_layout.txt --no-visual
```

Save solution to file:
```
python pacman_ai/src/main.py pacman_ai/layouts/mediumMaze.txt --output solution.txt
```

### Generating Random Layouts

You can generate random layouts using the utility script:

```
python pacman_ai/utils/generate_layout.py
```

This will print a random layout to the console. To save it to a file:

```
python pacman_ai/utils/generate_layout.py --width 30 --height 20 --filename pacman_ai/layouts/my_layout.txt
```

## Game Mechanics

### Basic Rules
- Pacman must collect all food dots (`.`) to complete the level
- Walls (`%`) block Pacman's movement unless he has eaten a magical pie
- Pacman can move North, South, East, West or Stop

### Special Features

#### Magical Pies
- Magical pies (`O`) allow Pacman to pass through walls for 5 steps
- If Pacman is inside a wall when the power wears off, he gets stuck and loses

#### Teleportation
- The four extreme corners of the maze are connected
- When Pacman reaches one corner, he teleports to the diagonally opposite corner

## Heuristics

The project implements two admissible heuristics for A* search:

### Minimum Food Distance (MFD)
- Calculates the Manhattan distance to the closest food dot
- Simple but less informed heuristic

### Minimum Spanning Tree (MST)
- Creates a minimum spanning tree connecting Pacman and all food dots
- More informed heuristic that accounts for the need to visit all food
- Default option as it typically provides better performance

## Visualization Controls

During visualization:
- Press any key to start the animation
- Press ESC to quit at any time
- After completion, press any key to exit

The visualization displays:
- Pacman's position and movement
- Remaining food dots and magical pies
- Wall status (active or vanished)
- Current step and action
- Special effects for eating food, teleportation, and wall phasing

## Implementation Details

### A* Search Algorithm
The A* search is implemented in `search.py`. It uses a priority queue to maintain the frontier and explores states in order of their estimated total cost.

### State Representation
Each state in the search space represents:
- Pacman's current position
- Remaining food dots and magical pies
- Whether walls are currently passable (and for how many more steps)
- Actions taken to reach this state
- Current path cost

### Successor Function
The successor function handles:
- Valid movement in four directions
- Collecting food dots and magical pies
- Teleportation at corners
- Wall phasing mechanic with temporary wall-passing ability

## License

[MIT License](LICENSE)

## Acknowledgments

This project was developed as an educational implementation of A* search for pathfinding problems.