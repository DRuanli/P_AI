"""
Visualization using Pygame for Pacman A* Search
"""
try:
    import pygame

    pygame_available = True
except ImportError:
    pygame_available = False
    print("Pygame not available. Install with 'pip install pygame' for visualization.")

import time
import sys


class PacmanVisualizer:
    """
    Visualizes the Pacman maze and solution path using Pygame
    """

    def __init__(self, maze, path=None, cell_size=20, fps=5):
        """
        Initialize the visualizer

        Args:
            maze (Maze): The maze to visualize
            path (list): List of states in solution path
            cell_size (int): Size of each cell in pixels
            fps (int): Frames per second for animation
        """
        if not pygame_available:
            raise ImportError("Pygame is required for visualization")

        self.maze = maze
        self.path = path or []
        self.cell_size = cell_size
        self.fps = fps

        # Calculate window dimensions
        self.width = maze.width * cell_size
        self.height = maze.height * cell_size

        # Define colors
        self.colors = {
            'wall': (0, 0, 255),  # Blue
            'food': (255, 255, 0),  # Yellow
            'pie': (255, 0, 255),  # Magenta
            'pacman': (255, 255, 0),  # Yellow
            'path': (255, 0, 0),  # Red
            'background': (0, 0, 0),  # Black
            'text': (255, 255, 255)  # White
        }

        # Initialize pygame
        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Pacman A* Search")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('Arial', 16)

    def run(self):
        """Run the visualization"""
        # Wait for key press to start animation
        self.draw_maze()
        pygame.display.flip()

        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                elif event.type == pygame.KEYDOWN:
                    waiting = False

        # Animate the solution
        self.animate_solution()

    def draw_maze(self):
        """Draw the maze"""
        # Clear screen
        self.screen.fill(self.colors['background'])

        # Draw grid
        for y in range(self.maze.height):
            for x in range(self.maze.width):
                rect = pygame.Rect(
                    x * self.cell_size,
                    y * self.cell_size,
                    self.cell_size,
                    self.cell_size
                )

                # Draw cell based on content
                if self.maze.is_wall(x, y):
                    pygame.draw.rect(self.screen, self.colors['wall'], rect)

                # Draw food
                if (x, y) in self.maze.food_positions:
                    center = (
                        x * self.cell_size + self.cell_size // 2,
                        y * self.cell_size + self.cell_size // 2
                    )
                    radius = self.cell_size // 8
                    pygame.draw.circle(self.screen, self.colors['food'], center, radius)

                # Draw magical pie
                if (x, y) in self.maze.magical_pie_positions:
                    center = (
                        x * self.cell_size + self.cell_size // 2,
                        y * self.cell_size + self.cell_size // 2
                    )
                    radius = self.cell_size // 4
                    pygame.draw.circle(self.screen, self.colors['pie'], center, radius)

        # Draw initial pacman position
        x, y = self.maze.pacman_start
        center = (
            x * self.cell_size + self.cell_size // 2,
            y * self.cell_size + self.cell_size // 2
        )
        radius = self.cell_size // 2 - 2
        pygame.draw.circle(self.screen, self.colors['pacman'], center, radius)

    def animate_solution(self):
        """Animate the solution path"""
        if not self.path:
            print("No path to animate")
            time.sleep(2)
            pygame.quit()
            return

        # Start with the first state
        current_state = self.path[0]
        remaining_food = self.maze.food_positions.copy()
        remaining_pies = self.maze.magical_pie_positions.copy()
        wall_pass_mode = False
        wall_pass_steps = 0

        # Loop through actions
        for action in current_state.path:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return

            # Clear screen and redraw maze
            self.screen.fill(self.colors['background'])

            # Draw grid with current state
            for y in range(self.maze.height):
                for x in range(self.maze.width):
                    rect = pygame.Rect(
                        x * self.cell_size,
                        y * self.cell_size,
                        self.cell_size,
                        self.cell_size
                    )

                    # Draw cell based on content
                    if self.maze.is_wall(x, y):
                        if wall_pass_mode:
                            # Draw transparent walls in wall-pass mode
                            s = pygame.Surface((self.cell_size, self.cell_size))
                            s.set_alpha(128)
                            s.fill(self.colors['wall'])
                            self.screen.blit(s, rect)
                        else:
                            pygame.draw.rect(self.screen, self.colors['wall'], rect)

                    # Draw remaining food
                    if (x, y) in remaining_food:
                        center = (
                            x * self.cell_size + self.cell_size // 2,
                            y * self.cell_size + self.cell_size // 2
                        )
                        radius = self.cell_size // 8
                        pygame.draw.circle(self.screen, self.colors['food'], center, radius)

                    # Draw remaining magical pies
                    if (x, y) in remaining_pies:
                        center = (
                            x * self.cell_size + self.cell_size // 2,
                            y * self.cell_size + self.cell_size // 2
                        )
                        radius = self.cell_size // 4
                        pygame.draw.circle(self.screen, self.colors['pie'], center, radius)

            # Get current position
            x, y = current_state.position

            # Apply the action
            if action == 'North':
                y -= 1
            elif action == 'East':
                x += 1
            elif action == 'South':
                y += 1
            elif action == 'West':
                x -= 1
            # 'Stop' action does nothing

            # Check for teleportation
            teleport_dest = self.maze.get_teleport_destination(x, y)
            if teleport_dest:
                x, y = teleport_dest

            # Update position
            current_state.position = (x, y)

            # Check for food collection
            if (x, y) in remaining_food:
                remaining_food.remove((x, y))

            # Check for magical pie collection
            if (x, y) in remaining_pies:
                remaining_pies.remove((x, y))
                wall_pass_mode = True
                wall_pass_steps = 5

            # Update wall_pass_steps
            if wall_pass_steps > 0:
                wall_pass_steps -= 1
                if wall_pass_steps == 0:
                    wall_pass_mode = False

            # Draw Pacman
            center = (
                x * self.cell_size + self.cell_size // 2,
                y * self.cell_size + self.cell_size // 2
            )
            radius = self.cell_size // 2 - 2

            # Draw Pacman differently if in wall-pass mode
            if wall_pass_mode:
                # Draw with glowing effect
                outer_radius = radius + 2
                pygame.draw.circle(self.screen, (255, 165, 0), center, outer_radius)

            pygame.draw.circle(self.screen, self.colors['pacman'], center, radius)

            # Draw status text
            text_surface = self.font.render(
                f"Action: {action}, Food left: {len(remaining_food)}, Wall-pass: {wall_pass_steps}",
                True,
                self.colors['text']
            )
            self.screen.blit(text_surface, (10, 10))

            # Update display
            pygame.display.flip()
            self.clock.tick(self.fps)

        # Display the end result for a while
        time.sleep(2)
        pygame.quit()