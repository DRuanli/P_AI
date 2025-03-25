import pygame
import time
import math
import random
from typing import Tuple, Set, List, Optional

# Enhanced colors with better contrast and visual appeal
BLACK = (0, 0, 0)
DARK_BLUE = (25, 25, 112)  # Midnight blue for background
WALL_BLUE = (65, 105, 225)  # Royal blue for walls
WALL_EDGE = (30, 60, 125)  # Darker blue for wall edges
YELLOW = (255, 255, 0)  # Bright yellow for Pacman
POWER_RED = (255, 50, 50)  # Brighter red for powered Pacman
WHITE = (255, 255, 255)  # White for food
FOOD_GLOW = (200, 200, 255)  # Light blue glow for food
GREEN = (50, 255, 50)  # Brighter green for magical pies
PURPLE = (180, 100, 255)  # Brighter purple for teleport corners
GRID_LINE = (40, 40, 60)  # Subtle grid lines
GOLD = (255, 215, 0)  # Gold for score particles
CYAN = (0, 255, 255)  # Cyan for wall phasing effects


class Visualizer:
    """Enhanced Pygame-based visualizer for Pacman A* search solutions."""

    def __init__(self, maze, cell_size: int = 30, step_delay: float = 0.2, logger=None):
        """Initialize visualizer with enhanced visuals"""
        self.maze = maze
        self.cell_size = cell_size
        # Add padding for info panel
        self.width = maze.width * cell_size
        self.height = maze.height * cell_size + 60  # Extra space for info panel
        self.step_delay = step_delay
        self.logger = logger
        self.animation_frame = 0  # For animations

        # Initialize pygame with better display settings
        pygame.init()
        pygame.display.set_caption('Pacman A* Pathfinding Visualization')
        self.screen = pygame.display.set_mode((self.width, self.height))

        # Better fonts
        self.title_font = pygame.font.SysFont('Arial', 24, bold=True)
        self.info_font = pygame.font.SysFont('Arial', 18)
        self.small_font = pygame.font.SysFont('Arial', 14)

        # Load or create sound effects
        try:
            self.eat_sound = pygame.mixer.Sound('eat.wav')
            self.power_sound = pygame.mixer.Sound('power.wav')
            self.teleport_sound = pygame.mixer.Sound('teleport.wav')
            self.wall_phase_sound = pygame.mixer.Sound('phase.wav')
            self.sounds_loaded = True
        except:
            self.sounds_loaded = False

        # Animation variables
        self.pacman_angle = 0  # For Pacman's mouth
        self.mouth_direction = 1  # Open or close
        self.last_action = None  # Track last action for rotation
        self.glow_value = 0  # For pulsing effects
        self.transition_pos = None  # For smooth movement
        self.transition_start = None
        self.transition_target = None
        self.transition_time = 0

        # Effect particles
        self.particles = []  # List of active particles
        self.wall_phase_effects = []  # List of wall phasing effects
        self.eat_effects = []  # List of food eating effects
        self.teleport_effects = []  # List of teleport effects
        self.power_wave = None  # Power wave effect

    def cell_to_pixel(self, x: int, y: int) -> Tuple[int, int]:
        """Convert maze coordinates to screen pixels"""
        return (x * self.cell_size + self.cell_size // 2,
                y * self.cell_size + self.cell_size // 2)

    def draw_wall(self, x: int, y: int, vanished: bool = False):
        """Draw enhanced wall with 3D effect and texture"""
        rect = pygame.Rect(
            x * self.cell_size,
            y * self.cell_size,
            self.cell_size,
            self.cell_size
        )

        if vanished:
            # Semi-transparent ghost walls
            s = pygame.Surface((self.cell_size, self.cell_size))
            s.set_alpha(40 + 20 * math.sin(self.animation_frame * 0.2))  # Pulsing transparency
            s.fill(WALL_BLUE)
            self.screen.blit(s, rect)

            # Wireframe edges
            pygame.draw.rect(self.screen, (WALL_BLUE[0], WALL_BLUE[1], WALL_BLUE[2], 80),
                             rect, 1)
        else:
            # Solid wall with 3D effect
            pygame.draw.rect(self.screen, WALL_BLUE, rect)

            # Draw subtle grid pattern
            for i in range(1, 3):
                pygame.draw.line(self.screen, WALL_EDGE,
                                 (rect.left, rect.top + i * self.cell_size // 3),
                                 (rect.right, rect.top + i * self.cell_size // 3), 1)
                pygame.draw.line(self.screen, WALL_EDGE,
                                 (rect.left + i * self.cell_size // 3, rect.top),
                                 (rect.left + i * self.cell_size // 3, rect.bottom), 1)

            # Highlight and shadow for 3D effect
            pygame.draw.line(self.screen, tuple(min(c + 30, 255) for c in WALL_BLUE),
                             (rect.left, rect.top), (rect.right - 1, rect.top), 2)
            pygame.draw.line(self.screen, tuple(min(c + 30, 255) for c in WALL_BLUE),
                             (rect.left, rect.top), (rect.left, rect.bottom - 1), 2)
            pygame.draw.line(self.screen, tuple(max(c - 30, 0) for c in WALL_BLUE),
                             (rect.right - 1, rect.top), (rect.right - 1, rect.bottom - 1), 2)
            pygame.draw.line(self.screen, tuple(max(c - 30, 0) for c in WALL_BLUE),
                             (rect.left, rect.bottom - 1), (rect.right - 1, rect.bottom - 1), 2)

    def draw_food(self, x: int, y: int):
        """Draw food with glowing effect"""
        center = self.cell_to_pixel(x, y)

        # Pulsing glow
        glow_size = 1 + 0.2 * math.sin(self.animation_frame * 0.2)
        glow_radius = int(self.cell_size // 6 * glow_size)

        # Draw outer glow
        for i in range(3):
            alpha = 90 - i * 30
            radius = glow_radius + i * 2
            s = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*FOOD_GLOW, alpha), (radius, radius), radius)
            self.screen.blit(s, (center[0] - radius, center[1] - radius))

        # Draw main food dot
        pygame.draw.circle(self.screen, WHITE, center, self.cell_size // 6)

    def draw_magical_pie(self, x: int, y: int):
        """Draw magical pie with spinning/glowing effect"""
        center = self.cell_to_pixel(x, y)

        # Pulsing outer glow
        glow_size = 1 + 0.3 * math.sin(self.animation_frame * 0.15)
        for i in range(4):
            alpha = 100 - i * 25
            radius = int(self.cell_size // 3 * glow_size) + i * 2
            s = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (GREEN[0], GREEN[1], GREEN[2], alpha), (radius, radius), radius)
            self.screen.blit(s, (center[0] - radius, center[1] - radius))

        # Draw spinning effect
        angle = self.animation_frame % 360
        radius = self.cell_size // 3
        for i in range(4):
            offset_angle = angle + (i * 90)
            x_offset = int(radius * 0.6 * math.cos(math.radians(offset_angle)))
            y_offset = int(radius * 0.6 * math.sin(math.radians(offset_angle)))
            pygame.draw.circle(self.screen, (*GREEN, 150),
                               (center[0] + x_offset, center[1] + y_offset),
                               self.cell_size // 10)

        # Center circle
        pygame.draw.circle(self.screen, GREEN, center, self.cell_size // 5)

    def draw_pacman(self, x: int, y: int, walls_vanished: int = 0, direction: str = None):
        """Draw Pacman with animated mouth and rotation"""
        # Set position (actual or transition)
        if self.transition_pos:
            center = self.transition_pos
        else:
            center = self.cell_to_pixel(x, y)

        # Set color based on power status
        color = POWER_RED if walls_vanished > 0 else YELLOW

        # Draw Pacman body with mouth animation
        # Pacman's mouth opens and closes as it moves
        mouth_angle = 45 + 30 * math.sin(self.animation_frame * 0.3)  # Animation range: 15° to 75°

        # Different rotations based on direction
        rotation = 0  # Default: facing right (East)
        if direction == 'North' or (self.last_action == 'North' and direction != 'Stop'):
            rotation = 90
        elif direction == 'West' or (self.last_action == 'West' and direction != 'Stop'):
            rotation = 180
        elif direction == 'South' or (self.last_action == 'South' and direction != 'Stop'):
            rotation = 270

        # Draw Pacman with mouth
        pygame.draw.circle(self.screen, color, center, self.cell_size // 2 - 2)

        # Draw mouth (pie slice)
        if direction != 'Stop':  # Only animate when moving
            start_angle = rotation - mouth_angle / 2
            end_angle = rotation + mouth_angle / 2

            mouth_points = [center]
            for angle in range(int(start_angle), int(end_angle + 1), 5):
                rad = math.radians(angle)
                x = center[0] + int((self.cell_size // 2) * math.cos(rad))
                y = center[1] - int((self.cell_size // 2) * math.sin(rad))
                mouth_points.append((x, y))

            if len(mouth_points) > 2:
                pygame.draw.polygon(self.screen, BLACK, mouth_points)

        # Show power indicator when walls are vanished
        if walls_vanished > 0:
            # Power number indicator
            radius = self.cell_size // 4
            pygame.draw.circle(self.screen, BLACK, center, radius)
            text = self.small_font.render(str(walls_vanished), True, WHITE)
            text_rect = text.get_rect(center=center)
            self.screen.blit(text, text_rect)

            # Pulsing power effect
            for i in range(3):
                pulse_size = 1 + 0.2 * math.sin(self.animation_frame * 0.3)
                radius = int(self.cell_size // 2 * pulse_size) + i * 3
                s = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
                alpha = 40 - i * 10
                pygame.draw.circle(s, (POWER_RED[0], POWER_RED[1], POWER_RED[2], alpha),
                                   (radius, radius), radius)
                self.screen.blit(s, (center[0] - radius, center[1] - radius))

    def draw_teleport_effect(self, pos1, pos2):
        """Draw teleportation effect between two points"""
        # Convert positions to pixel coordinates
        start = self.cell_to_pixel(*pos1)
        end = self.cell_to_pixel(*pos2)

        # Draw teleport beam
        for i in range(10):
            progress = i / 10
            mid_x = start[0] + (end[0] - start[0]) * progress
            mid_y = start[1] + (end[1] - start[1]) * progress
            radius = 3 + 2 * math.sin(self.animation_frame * 0.3 + i)
            alpha = 200 - i * 20
            s = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (PURPLE[0], PURPLE[1], PURPLE[2], alpha), (radius, radius), radius)
            self.screen.blit(s, (mid_x - radius, mid_y - radius))

    def draw_corner(self, x, y):
        """Draw teleport corner with subtle effect"""
        rect = pygame.Rect(
            x * self.cell_size,
            y * self.cell_size,
            self.cell_size,
            self.cell_size
        )

        # Draw corner marker
        pygame.draw.rect(self.screen, PURPLE, rect, 2)

        # Add subtle portal effect
        center = self.cell_to_pixel(x, y)
        for i in range(3):
            angle = (self.animation_frame * 5 + i * 120) % 360
            radius = self.cell_size // 3
            ox = int(radius * 0.5 * math.cos(math.radians(angle)))
            oy = int(radius * 0.5 * math.sin(math.radians(angle)))
            pygame.draw.circle(self.screen, (*PURPLE, 50), (center[0] + ox, center[1] + oy), 2)

    def draw_info_panel(self, step, total_steps, action, walls_vanished, food_left):
        """Draw enhanced information panel at the bottom"""
        panel_rect = pygame.Rect(0, self.height - 60, self.width, 60)

        # Draw panel background
        pygame.draw.rect(self.screen, DARK_BLUE, panel_rect)
        pygame.draw.line(self.screen, WALL_BLUE, (0, self.height - 60), (self.width, self.height - 60), 2)

        # Draw information text
        title = self.title_font.render(f"Pacman A* Search Visualization", True, WHITE)
        self.screen.blit(title, (10, self.height - 55))

        # Step info
        step_info = self.info_font.render(f"Step: {step}/{total_steps}", True, WHITE)
        self.screen.blit(step_info, (10, self.height - 30))

        # Action
        action_info = self.info_font.render(f"Action: {action}", True, YELLOW)
        self.screen.blit(action_info, (150, self.height - 30))

        # Food left
        food_info = self.info_font.render(f"Food left: {food_left}", True, WHITE)
        self.screen.blit(food_info, (300, self.height - 30))

        # Wall status
        if walls_vanished > 0:
            status = f"Walls Vanished: {walls_vanished} steps"
            color = POWER_RED
        else:
            status = "Walls Active"
            color = WALL_BLUE
        status_info = self.info_font.render(status, True, color)
        self.screen.blit(status_info, (450, self.height - 30))

    def create_food_particles(self, x, y, count=12):
        """Create particles for food eating effect"""
        center = self.cell_to_pixel(x, y)
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1, 3)
            size = random.uniform(1, 3)
            lifetime = random.uniform(0.5, 1.0)
            self.particles.append({
                'x': center[0],
                'y': center[1],
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'size': size,
                'color': WHITE,
                'fade': 255,
                'lifetime': lifetime,
                'elapsed': 0
            })
        # Add score pop-up
        self.eat_effects.append({
            'x': center[0],
            'y': center[1],
            'text': '+10',
            'color': GOLD,
            'size': 16,
            'vy': -1.5,
            'lifetime': 1.0,
            'elapsed': 0
        })

    def create_power_particles(self, x, y, count=30):
        """Create particles for power pill eating effect"""
        center = self.cell_to_pixel(x, y)
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 5)
            size = random.uniform(2, 4)
            lifetime = random.uniform(1.0, 2.0)
            self.particles.append({
                'x': center[0],
                'y': center[1],
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'size': size,
                'color': GREEN,
                'fade': 255,
                'lifetime': lifetime,
                'elapsed': 0
            })
        # Add power wave effect
        self.power_wave = {
            'x': center[0],
            'y': center[1],
            'radius': 0,
            'max_radius': self.cell_size * 8,
            'color': (GREEN[0], GREEN[1], GREEN[2], 180),
            'lifetime': 1.0,
            'elapsed': 0
        }
        # Add score pop-up
        self.eat_effects.append({
            'x': center[0],
            'y': center[1],
            'text': 'POWER!',
            'color': GREEN,
            'size': 20,
            'vy': -2,
            'lifetime': 1.5,
            'elapsed': 0
        })

    def create_wall_phase_effect(self, x, y, direction):
        """Create effect for passing through a wall"""
        center = self.cell_to_pixel(x, y)
        dx, dy = 0, 0
        if direction == 'North':
            dy = self.cell_size // 2
        elif direction == 'South':
            dy = -self.cell_size // 2
        elif direction == 'East':
            dx = -self.cell_size // 2
        elif direction == 'West':
            dx = self.cell_size // 2

        # Create ripple effect at wall intersection
        self.wall_phase_effects.append({
            'x': center[0] + dx,
            'y': center[1] + dy,
            'radius': 2,
            'max_radius': self.cell_size * 0.8,
            'color': CYAN,
            'lifetime': 0.8,
            'elapsed': 0
        })

        # Create ghost trail particles
        for i in range(6):
            offset = i * 0.15
            self.particles.append({
                'x': center[0] - dx * offset * 2,
                'y': center[1] - dy * offset * 2,
                'vx': -dx * 0.05,
                'vy': -dy * 0.05,
                'size': self.cell_size // 3,
                'color': YELLOW if self.walls_vanished == 0 else POWER_RED,
                'fade': 100,
                'lifetime': 0.5 - i * 0.05,
                'elapsed': 0,
                'is_ghost': True
            })

    def create_teleport_effect(self, from_pos, to_pos):
        """Create teleportation effect between two points"""
        from_pixel = self.cell_to_pixel(*from_pos)
        to_pixel = self.cell_to_pixel(*to_pos)

        # Create disappearing effect at source
        for _ in range(20):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(3, 6)
            size = random.uniform(2, 4)
            lifetime = random.uniform(0.3, 0.7)
            self.particles.append({
                'x': from_pixel[0],
                'y': from_pixel[1],
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'size': size,
                'color': PURPLE,
                'fade': 255,
                'lifetime': lifetime,
                'elapsed': 0
            })

        # Create appearing effect at destination
        for _ in range(20):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1, 3)
            size = random.uniform(3, 5)
            lifetime = random.uniform(0.5, 1.0)
            # Particles converge toward center
            self.particles.append({
                'x': to_pixel[0] + math.cos(angle) * self.cell_size,
                'y': to_pixel[1] + math.sin(angle) * self.cell_size,
                'vx': -math.cos(angle) * speed,
                'vy': -math.sin(angle) * speed,
                'size': size,
                'color': PURPLE,
                'fade': 255,
                'lifetime': lifetime,
                'elapsed': 0
            })

        # Create teleport beam effect
        self.teleport_effects.append({
            'from': from_pixel,
            'to': to_pixel,
            'width': 8,
            'color': PURPLE,
            'lifetime': 0.8,
            'elapsed': 0
        })

        # Add teleport text
        self.eat_effects.append({
            'x': to_pixel[0],
            'y': to_pixel[1] - self.cell_size // 2,
            'text': 'TELEPORT!',
            'color': PURPLE,
            'size': 18,
            'vy': -1.5,
            'lifetime': 1.0,
            'elapsed': 0
        })

    def update_particles(self, delta_time):
        """Update and draw all particle effects"""
        # Update regular particles
        for particle in self.particles[:]:
            particle['elapsed'] += delta_time
            if particle['elapsed'] >= particle['lifetime']:
                self.particles.remove(particle)
                continue

            # Update position
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']

            # Update fade
            progress = particle['elapsed'] / particle['lifetime']
            particle['fade'] = int(255 * (1 - progress))

            # Draw particle
            if particle.get('is_ghost', False):
                # Ghost trail (semi-transparent circle)
                size = particle['size'] * (1 - progress * 0.5)
                s = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                pygame.draw.circle(s, (*particle['color'], particle['fade']),
                                   (size, size), size)
                self.screen.blit(s, (particle['x'] - size, particle['y'] - size))
            else:
                # Regular particle (small circle)
                size = particle['size'] * (1 - progress * 0.3)
                s = pygame.Surface((max(1, int(size * 2)), max(1, int(size * 2))), pygame.SRCALPHA)
                pygame.draw.circle(s, (*particle['color'], particle['fade']),
                                   (max(1, int(size)), max(1, int(size))), max(1, int(size)))
                self.screen.blit(s, (particle['x'] - size, particle['y'] - size))

        # Update wall phase effects
        for effect in self.wall_phase_effects[:]:
            effect['elapsed'] += delta_time
            if effect['elapsed'] >= effect['lifetime']:
                self.wall_phase_effects.remove(effect)
                continue

            # Update radius
            progress = effect['elapsed'] / effect['lifetime']
            radius = effect['max_radius'] * progress
            alpha = int(180 * (1 - progress))
            # Draw ripple effect
            s = pygame.Surface((int(radius * 2), int(radius * 2)), pygame.SRCALPHA)
            pygame.draw.circle(s, (*effect['color'], alpha), (int(radius), int(radius)), int(radius), 2)
            self.screen.blit(s, (effect['x'] - radius, effect['y'] - radius))

        # Update eat effects (score popups)
        for effect in self.eat_effects[:]:
            effect['elapsed'] += delta_time
            if effect['elapsed'] >= effect['lifetime']:
                self.eat_effects.remove(effect)
                continue

            # Update position
            effect['y'] += effect['vy']

            # Update fade
            progress = effect['elapsed'] / effect['lifetime']
            alpha = int(255 * (1 - progress))

            # Draw text
            font = pygame.font.SysFont('Arial', effect['size'], bold=True)
            text = font.render(effect['text'], True, effect['color'])
            text.set_alpha(alpha)
            text_rect = text.get_rect(center=(effect['x'], effect['y']))
            self.screen.blit(text, text_rect)

        # Update teleport beam effects
        for effect in self.teleport_effects[:]:
            effect['elapsed'] += delta_time
            if effect['elapsed'] >= effect['lifetime']:
                self.teleport_effects.remove(effect)
                continue

            # Calculate progress
            progress = effect['elapsed'] / effect['lifetime']
            alpha = int(200 * (1 - progress))
            width = max(1, int(effect['width'] * (1 - progress * 0.7)))

            # Draw beam
            s = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            pygame.draw.line(s, (*effect['color'], alpha),
                             effect['from'], effect['to'], width)

            # Add sparkles along the beam
            beam_length = math.sqrt((effect['to'][0] - effect['from'][0]) ** 2 +
                                    (effect['to'][1] - effect['from'][1]) ** 2)
            num_sparkles = max(2, int(beam_length / 20))

            for i in range(num_sparkles):
                t = random.uniform(0, 1)
                sparkle_x = effect['from'][0] + t * (effect['to'][0] - effect['from'][0])
                sparkle_y = effect['from'][1] + t * (effect['to'][1] - effect['from'][1])
                sparkle_size = random.uniform(2, 4) * (1 - progress)
                pygame.draw.circle(s, (*effect['color'], alpha),
                                   (int(sparkle_x), int(sparkle_y)),
                                   int(sparkle_size))

            self.screen.blit(s, (0, 0))

        # Update power wave effect
        if self.power_wave:
            self.power_wave['elapsed'] += delta_time
            if self.power_wave['elapsed'] >= self.power_wave['lifetime']:
                self.power_wave = None
            else:
                # Update radius
                progress = self.power_wave['elapsed'] / self.power_wave['lifetime']
                radius = self.power_wave['max_radius'] * progress
                alpha = int(180 * (1 - progress))

                # Draw wave effect
                s = pygame.Surface((int(radius * 2), int(radius * 2)), pygame.SRCALPHA)
                color = (self.power_wave['color'][0], self.power_wave['color'][1],
                         self.power_wave['color'][2], alpha)
                pygame.draw.circle(s, color, (int(radius), int(radius)), int(radius),
                                   max(1, int(5 * (1 - progress))))
                self.screen.blit(s, (self.power_wave['x'] - radius, self.power_wave['y'] - radius))

    def draw_maze(self, pacman_pos, remaining_food, remaining_magical_pies,
                  walls_vanished_steps, action=None, step=0, total_steps=0):
        """Draw the current state of the maze with enhanced visuals"""
        # Store current walls_vanished state for effects
        self.walls_vanished = walls_vanished_steps

        # Fill the screen with background
        self.screen.fill(BLACK)

        # Update animation frame
        self.animation_frame += 1

        # Draw subtle grid
        for x in range(self.maze.width + 1):
            pygame.draw.line(self.screen, GRID_LINE,
                             (x * self.cell_size, 0),
                             (x * self.cell_size, self.height - 60), 1)
        for y in range(self.maze.height + 1):
            pygame.draw.line(self.screen, GRID_LINE,
                             (0, y * self.cell_size),
                             (self.width, y * self.cell_size), 1)

        # Draw maze elements
        for y in range(self.maze.height):
            for x in range(self.maze.width):
                # Draw walls
                if self.maze.is_wall(x, y):
                    self.draw_wall(x, y, walls_vanished_steps > 0)

                # Draw corners
                if self.maze.is_corner(x, y):
                    self.draw_corner(x, y)

        # Draw food points with enhanced visuals
        for x, y in remaining_food:
            self.draw_food(x, y)

        # Draw magical pies with enhanced visuals
        for x, y in remaining_magical_pies:
            self.draw_magical_pie(x, y)

        # Draw Pacman with animation
        pacman_x, pacman_y = pacman_pos
        self.draw_pacman(pacman_x, pacman_y, walls_vanished_steps, action)

        # Draw all particle effects
        self.update_particles(min(0.05, self.step_delay / 3))

        # Draw info panel
        self.draw_info_panel(step, total_steps, action, walls_vanished_steps, len(remaining_food))

        # Update display
        pygame.display.flip()

    def start_transition(self, from_pos, to_pos, duration=0.1):
        """Start a smooth transition between positions"""
        from_pixel = self.cell_to_pixel(*from_pos)
        to_pixel = self.cell_to_pixel(*to_pos)
        self.transition_start = from_pixel
        self.transition_target = to_pixel
        self.transition_time = 0
        self.transition_duration = duration
        self.transition_pos = from_pixel

    def update_transition(self, delta_time):
        """Update position transition"""
        if not self.transition_start:
            return False

        self.transition_time += delta_time
        progress = min(1.0, self.transition_time / self.transition_duration)

        # Smooth easing function
        progress = 0.5 - 0.5 * math.cos(progress * math.pi)

        # Calculate new position
        x = self.transition_start[0] + (self.transition_target[0] - self.transition_start[0]) * progress
        y = self.transition_start[1] + (self.transition_target[1] - self.transition_start[1]) * progress
        self.transition_pos = (x, y)

        # Check if transition is complete
        if progress >= 1.0:
            self.transition_start = None
            self.transition_pos = None
            return False

        return True

    def visualize_solution(self, actions: List[str]) -> None:
        """Animate the solution with enhanced visuals and effects"""
        if not actions:
            print("No solution to visualize")
            if self.logger: self.logger.warning("No solution to visualize")
            return

        # Initialize game state
        pacman_pos = self.maze.pacman_start
        remaining_food = set(self.maze.food_points)
        remaining_magical_pies = set(self.maze.magical_pies)
        walls_vanished_steps = 0

        # Draw initial state
        self.draw_maze(pacman_pos, remaining_food, remaining_magical_pies,
                       walls_vanished_steps, None, 0, len(actions))

        # Wait for key press to start
        print("Press any key to start animation. Press ESC to quit.")
        if self.logger: self.logger.info("Visualization ready, waiting for key press to start")

        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    if self.logger: self.logger.info("Visualization cancelled before start")
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        if self.logger: self.logger.info("Visualization cancelled before start")
                        return
                    waiting = False

        if self.logger: self.logger.info("Visualization started")

        # Execute actions
        step, game_over = 0, False

        # Game loop
        last_time = time.time()

        for action in actions:
            step += 1
            if self.logger and step % 20 == 0:
                self.logger.info(f"Visualization step {step}/{len(actions)}, Action: {action}")

            # Update position based on action
            x, y = pacman_pos
            new_pos = pacman_pos

            # Apply movement
            if action == 'North':
                new_pos = (x, y - 1)
            elif action == 'East':
                new_pos = (x + 1, y)
            elif action == 'South':
                new_pos = (x, y + 1)
            elif action == 'West':
                new_pos = (x - 1, y)

            # Start transition if position changed
            if new_pos != pacman_pos and action != 'Stop':
                self.start_transition(pacman_pos, new_pos)
                self.last_action = action

            # Check if passing through a wall before updating position
            wall_phased = False
            if self.maze.is_wall(*new_pos) and walls_vanished_steps > 0 and new_pos != pacman_pos:
                wall_phased = True
                self.create_wall_phase_effect(*pacman_pos, action)
                if self.sounds_loaded:
                    self.wall_phase_sound.play()

            # Update position and check wall vanishing
            if new_pos != pacman_pos:
                pacman_pos = new_pos
                if walls_vanished_steps > 0:
                    walls_vanished_steps -= 1
                    # Check if trapped in wall
                    if walls_vanished_steps == 0 and self.maze.is_wall(*pacman_pos):
                        game_over = True
                        msg = "GAME OVER: Pacman got stuck in a wall when walls reappeared!"
                        print(msg)
                        if self.logger: self.logger.warning(msg)
                        break

            # Check for teleportation
            teleported = False
            if self.maze.is_corner(*pacman_pos):
                teleport_pos = self.maze.get_opposite_corner(*pacman_pos)
                if teleport_pos and teleport_pos != pacman_pos:  # Make sure it's actually teleporting
                    if self.logger: self.logger.info(f"Teleportation from {pacman_pos} to {teleport_pos}")
                    # Play teleport effect
                    if self.sounds_loaded:
                        self.teleport_sound.play()
                    # Create teleport effect
                    self.create_teleport_effect(pacman_pos, teleport_pos)
                    # Keep track of positions for teleport effect
                    from_pos = pacman_pos
                    pacman_pos = teleport_pos
                    teleported = True

            # Handle food collection
            food_eaten = False
            if pacman_pos in remaining_food:
                if self.logger: self.logger.info(f"Food eaten at {pacman_pos}, {len(remaining_food) - 1} remaining")
                self.create_food_particles(*pacman_pos)
                remaining_food.remove(pacman_pos)
                food_eaten = True
                if self.sounds_loaded:
                    self.eat_sound.play()

            # Handle magical pie effects
            power_eaten = False
            if pacman_pos in remaining_magical_pies:
                if self.logger: self.logger.info(f"Magical pie eaten at {pacman_pos}, walls vanished for 5 steps")
                self.create_power_particles(*pacman_pos)
                remaining_magical_pies.remove(pacman_pos)
                walls_vanished_steps = 5
                power_eaten = True
                if self.sounds_loaded:
                    self.power_sound.play()

            # Animation loop
            transition_active = True
            start_time = time.time()

            while transition_active:
                current_time = time.time()
                delta_time = current_time - last_time
                last_time = current_time

                # Process events during transition
                for event in pygame.event.get():
                    if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                        pygame.quit()
                        if self.logger: self.logger.info(f"Visualization interrupted at step {step}/{len(actions)}")
                        return

                # Update position transition
                transition_active = self.update_transition(delta_time) if self.transition_start else False

                # Draw current state with transition
                self.draw_maze(pacman_pos, remaining_food, remaining_magical_pies,
                               walls_vanished_steps, action, step, len(actions))

                # Draw teleport effect if teleported
                if teleported:
                    self.draw_teleport_effect(from_pos, pacman_pos)

                # Ensure frame rate
                elapsed = time.time() - start_time
                if elapsed < self.step_delay:
                    time.sleep(max(0.01, min(self.step_delay - elapsed, 0.05)))
                else:
                    # Finish animation if taking too long
                    transition_active = False

            # Final draw of current state after transition
            self.draw_maze(pacman_pos, remaining_food, remaining_magical_pies,
                           walls_vanished_steps, action, step, len(actions))

            # Check for exit
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    pygame.quit()
                    if self.logger: self.logger.info(f"Visualization interrupted at step {step}/{len(actions)}")
                    return

            # Add delay between steps
            time.sleep(max(0, self.step_delay - (time.time() - last_time)))
            last_time = time.time()

        # Show completion message
        completion_font = pygame.font.SysFont('Arial', 36, bold=True)

        if game_over:
            completion_text = "GAME OVER: Pacman got stuck in a wall!"
            text_color = POWER_RED
            if self.logger: self.logger.warning("Game Over - Pacman got stuck in a wall when walls reappeared!")
        else:
            completion_text = f"Solution completed in {step} steps!"
            text_color = GREEN
            if self.logger: self.logger.info(f"Solution completed successfully in {step} steps!")
            if remaining_food:
                food_msg = f"Warning: {len(remaining_food)} food dots remain uneaten."
                if self.logger: self.logger.warning(food_msg)

        # Display completion message overlay
        s = pygame.Surface((self.width, 80))
        s.set_alpha(200)
        s.fill(BLACK)
        self.screen.blit(s, (0, self.height // 2 - 40))

        text = completion_font.render(completion_text, True, text_color)
        text_rect = text.get_rect(center=(self.width // 2, self.height // 2))
        self.screen.blit(text, text_rect)

        # Show "Press any key to exit" message
        exit_text = self.info_font.render("Press any key to exit", True, WHITE)
        exit_rect = exit_text.get_rect(center=(self.width // 2, self.height // 2 + 30))
        self.screen.blit(exit_text, exit_rect)

        pygame.display.flip()

        if self.logger: self.logger.info("Visualization complete, waiting for key press to exit")

        # Wait for key press to exit
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or event.type == pygame.KEYDOWN:
                    waiting = False

        pygame.quit()
        if self.logger: self.logger.info("Visualization closed")