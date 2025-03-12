import pygame
import time

# Define colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
PURPLE = (128, 0, 128)


class Visualizer:
    def __init__(self, maze, cell_size=20):
        """Initialize the visualizer with the maze and cell size"""
        self.maze = maze
        self.cell_size = cell_size
        self.width = maze.width * cell_size
        self.height = maze.height * cell_size

        # Initialize pygame
        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption('Pacman A* Search')
        self.font = pygame.font.SysFont('Arial', 16)

    def draw_maze(self, pacman_pos, remaining_food, remaining_magical_pies, wall_pass_steps):
        """Draw the current state of the maze"""
        # Fill the screen with black
        self.screen.fill(BLACK)

        # Draw the maze elements
        for y in range(self.maze.height):
            for x in range(self.maze.width):
                rect = pygame.Rect(
                    x * self.cell_size,
                    y * self.cell_size,
                    self.cell_size,
                    self.cell_size
                )

                # Draw walls
                if self.maze.is_wall(x, y):
                    pygame.draw.rect(self.screen, BLUE, rect)

                # Draw corner markers (for visualization purposes)
                if self.maze.is_corner(x, y):
                    pygame.draw.rect(self.screen, PURPLE, rect, 2)

        # Draw food points
        for x, y in remaining_food:
            center = (
                x * self.cell_size + self.cell_size // 2,
                y * self.cell_size + self.cell_size // 2
            )
            pygame.draw.circle(self.screen, WHITE, center, self.cell_size // 6)

        # Draw magical pies
        for x, y in remaining_magical_pies:
            center = (
                x * self.cell_size + self.cell_size // 2,
                y * self.cell_size + self.cell_size // 2
            )
            pygame.draw.circle(self.screen, GREEN, center, self.cell_size // 3)

        # Draw Pacman
        pacman_x, pacman_y = pacman_pos
        center = (
            pacman_x * self.cell_size + self.cell_size // 2,
            pacman_y * self.cell_size + self.cell_size // 2
        )

        # Draw Pacman with different color if it has wall-passing ability
        if wall_pass_steps > 0:
            pygame.draw.circle(self.screen, RED, center, self.cell_size // 2 - 2)
            # Display remaining wall pass steps
            text = self.font.render(str(wall_pass_steps), True, WHITE)
            text_rect = text.get_rect(center=center)
            self.screen.blit(text, text_rect)
        else:
            pygame.draw.circle(self.screen, YELLOW, center, self.cell_size // 2 - 2)

        # Update the display
        pygame.display.flip()

    def visualize_solution(self, actions):
        """Visualize the solution by showing Pacman's movements"""
        if not actions:
            print("No solution to visualize")
            return

        # Initialize the state
        pacman_pos = self.maze.pacman_start
        remaining_food = set(self.maze.food_points)
        remaining_magical_pies = set(self.maze.magical_pies)
        wall_pass_steps = 0

        # Draw the initial state
        self.draw_maze(pacman_pos, remaining_food, remaining_magical_pies, wall_pass_steps)

        # Display instructions
        print("Press any key to start animation. Press ESC to quit.")

        # Wait for a key press to start
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        return
                    waiting = False

        # Execute the actions
        step = 0
        for action in actions:
            step += 1
            # Update Pacman's position based on the action
            x, y = pacman_pos
            new_pos = pacman_pos

            if action == 'North':
                new_pos = (x, y - 1)
            elif action == 'East':
                new_pos = (x + 1, y)
            elif action == 'South':
                new_pos = (x, y + 1)
            elif action == 'West':
                new_pos = (x - 1, y)
            # 'Stop' action doesn't change position

            # Update position (if it changed)
            if new_pos != pacman_pos:
                pacman_pos = new_pos
                # Decrease wall pass steps when moving
                if wall_pass_steps > 0:
                    wall_pass_steps -= 1

            # Check for teleportation
            if self.maze.is_corner(*pacman_pos):
                teleport_pos = self.maze.get_opposite_corner(*pacman_pos)
                if teleport_pos:
                    pacman_pos = teleport_pos

            # Check if Pacman ate food
            if pacman_pos in remaining_food:
                remaining_food.remove(pacman_pos)

            # Check if Pacman ate a magical pie
            if pacman_pos in remaining_magical_pies:
                remaining_magical_pies.remove(pacman_pos)
                wall_pass_steps = 5  # Reset wall pass counter

            # Draw the updated state
            self.draw_maze(pacman_pos, remaining_food, remaining_magical_pies, wall_pass_steps)

            # Display step information
            pygame.display.set_caption(f'Pacman A* Search - Step {step}/{len(actions)} - Action: {action}')

            # Process events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    return

            # Add a short delay between steps
            time.sleep(0.3)

        # Display completion message
        print(f"Solution completed in {step} steps!")

        # Wait for a key press to exit
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or event.type == pygame.KEYDOWN:
                    waiting = False

        pygame.quit()