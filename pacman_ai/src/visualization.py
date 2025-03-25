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
RED = (255, 0, 0)  # Red for first ghost
BLUE = (0, 0, 255)  # Blue for second ghost
GHOST_COLORS = [RED, BLUE]  # Colors for the ghosts
SCARED_GHOST = (50, 50, 255)  # Blue for scared ghosts
FRUIT_COLOR = (255, 150, 0)  # Orange for fruits
TELEPORT_PAD_COLOR = (190, 120, 255)  # Bright purple for teleport pads
SLOW_PILL_COLOR = (100, 200, 255)  # Light blue for slow pills
SPEED_BOOST_COLOR = (255, 100, 100)  # Pinkish red for speed boosts
MOVING_WALL_ACTIVE = (150, 0, 150)  # Purple for active moving walls
MOVING_WALL_INACTIVE = (80, 0, 80)  # Darker purple for inactive moving walls


class Visualizer:
    """Enhanced Pygame-based visualizer for Pacman A* search solutions."""

    def __init__(self, maze, cell_size: int = 30, step_delay: float = 0.2,
                 logger=None, user_mode: bool = False):
        """Initialize visualizer with enhanced visuals"""
        self.maze = maze
        self.cell_size = cell_size
        # Add padding for info panel
        self.width = maze.width * cell_size
        self.height = maze.height * cell_size + 60  # Extra space for info panel
        self.step_delay = step_delay
        self.logger = logger
        self.animation_frame = 0  # For animations

        # User mode variables
        self.user_mode = user_mode
        self.game_over = False
        self.score = 0
        self.lives = 3
        self.paused = False

        # Power-up status
        self.ghosts_scared = False
        self.slow_motion_active = False
        self.speed_boost_active = False
        self.walls_vanished = False
        self.moving_walls_active = True

        # Fruit variables
        self.active_fruits = set()
        self.fruit_spawn_timer = 0
        self.fruit_spawn_interval = 15  # Spawn fruit every 15 seconds
        self.fruit_duration = 10  # Fruit stays for 10 seconds

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
            self.death_sound = pygame.mixer.Sound('death.wav')
            self.fruit_sound = pygame.mixer.Sound('fruit.wav')
            self.ghost_eat_sound = pygame.mixer.Sound('ghost_eat.wav')
            self.slow_motion_sound = pygame.mixer.Sound('slow.wav')
            self.speed_boost_sound = pygame.mixer.Sound('speed.wav')
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
        self.time_distortion = 0  # For slow motion effect
        self.speed_lines = []  # For speed boost effect
        self.moving_wall_offset = 0  # For moving wall animation

        # Effect particles
        self.particles = []  # List of active particles
        self.wall_phase_effects = []  # List of wall phasing effects
        self.eat_effects = []  # List of food eating effects
        self.teleport_effects = []  # List of teleport effects
        self.power_wave = None  # Power wave effect
        self.slow_motion_wave = None  # Slow motion wave effect
        self.speed_boost_wave = None  # Speed boost wave effect
        self.fruit_particles = []  # Fruit effect particles
        self.ghost_eaten_effects = []  # Ghost eating effects
        self.matrix_effect = []  # Matrix-like time distortion effect

    def cell_to_pixel(self, x: int, y: int) -> Tuple[int, int]:
        """Convert maze coordinates to screen pixels"""
        return (x * self.cell_size + self.cell_size // 2,
                y * self.cell_size + self.cell_size // 2)

    def draw_wall(self, x: int, y: int, vanished: bool = False, moving: bool = False, active: bool = True):
        """
        Draw enhanced wall with 3D effect and texture

        Args:
            x, y: Wall position
            vanished: Whether wall is in vanished state
            moving: Whether this is a moving wall
            active: Whether the moving wall is currently active/solid
        """
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
        elif moving:
            # Moving walls have special appearance
            color = MOVING_WALL_ACTIVE if active else MOVING_WALL_INACTIVE

            # Add animation effect for moving walls
            offset = int(3 * math.sin(self.animation_frame * 0.1))
            animated_rect = rect.copy()

            if active:
                # When active, oscillate in position slightly
                animated_rect.x += offset
                animated_rect.y += offset

                # Draw base
                pygame.draw.rect(self.screen, color, animated_rect)

                # Draw animated pattern
                pattern_offset = (self.animation_frame // 5) % 4
                for i in range(4):
                    line_pos = (i + pattern_offset) % 4
                    line_y = animated_rect.top + line_pos * self.cell_size // 4
                    pygame.draw.line(
                        self.screen,
                        (color[0] + 50, color[1] + 50, color[2] + 50),
                        (animated_rect.left, line_y),
                        (animated_rect.right, line_y),
                        2
                    )
            else:
                # When inactive, draw as semi-transparent with dashed lines
                s = pygame.Surface((self.cell_size, self.cell_size))
                s.set_alpha(120)
                s.fill(color)
                self.screen.blit(s, animated_rect)

                # Draw dashed outline
                dash_length = 4
                for i in range(0, self.cell_size, dash_length * 2):
                    # Top
                    pygame.draw.line(
                        self.screen,
                        WHITE,
                        (animated_rect.left + i, animated_rect.top),
                        (animated_rect.left + i + dash_length, animated_rect.top),
                        1
                    )
                    # Bottom
                    pygame.draw.line(
                        self.screen,
                        WHITE,
                        (animated_rect.left + i, animated_rect.bottom - 1),
                        (animated_rect.left + i + dash_length, animated_rect.bottom - 1),
                        1
                    )
                    # Left
                    pygame.draw.line(
                        self.screen,
                        WHITE,
                        (animated_rect.left, animated_rect.top + i),
                        (animated_rect.left, animated_rect.top + i + dash_length),
                        1
                    )
                    # Right
                    pygame.draw.line(
                        self.screen,
                        WHITE,
                        (animated_rect.right - 1, animated_rect.top + i),
                        (animated_rect.right - 1, animated_rect.top + i + dash_length),
                        1
                    )
        else:
            # Regular solid wall with 3D effect
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

    def draw_ghost(self, x: int, y: int, ghost_index: int = 0, scared: bool = False):
        """
        Draw a ghost character with animation

        Args:
            x, y: Ghost position
            ghost_index: Index for ghost color
            scared: Whether the ghost is in scared mode
        """
        center = self.cell_to_pixel(x, y)

        # Determine ghost color based on state
        if scared:
            # Flashing animation when scared
            if self.animation_frame % 10 < 5:
                color = SCARED_GHOST
            else:
                color = (230, 230, 255)  # White-blue flashing
        else:
            color = GHOST_COLORS[ghost_index % len(GHOST_COLORS)]

        # Basic ghost body with bobbing animation
        bob_offset = int(2 * math.sin(self.animation_frame * 0.2))
        radius = self.cell_size // 2 - 2

        # Additional effects for scared ghosts
        if scared:
            # Add shaking effect
            shake_x = random.randint(-1, 1)
            shake_y = random.randint(-1, 1)
            center = (center[0] + shake_x, center[1] + shake_y)

            # Add scared ghost particles
            if random.random() < 0.2:
                self.particles.append({
                    'x': center[0] + random.randint(-radius, radius),
                    'y': center[1] + random.randint(-radius, radius),
                    'vx': random.uniform(-0.5, 0.5),
                    'vy': random.uniform(-1, -0.2),
                    'size': random.uniform(1, 3),
                    'color': SCARED_GHOST,
                    'fade': 150,
                    'lifetime': random.uniform(0.3, 0.7),
                    'elapsed': 0
                })

        # Draw ghost body (semi-circle and rectangle)
        body_rect = pygame.Rect(
            center[0] - radius,
            center[1] - radius + bob_offset,
            radius * 2,
            radius * 1.2
        )

        # Draw ghost head (semi-circle)
        pygame.draw.circle(
            self.screen,
            color,
            (center[0], center[1] - radius * 0.2 + bob_offset),
            radius
        )

        # Draw ghost body (rectangle)
        pygame.draw.rect(
            self.screen,
            color,
            body_rect
        )

        # Draw ghost skirt (waves at bottom)
        wave_height = radius * 0.3
        bottom = body_rect.bottom
        segments = 6
        segment_width = radius * 2 / segments

        for i in range(segments):
            x_left = body_rect.left + i * segment_width
            x_right = x_left + segment_width

            # Scared ghosts have more pronounced wave animation
            if scared:
                wave_offset = int(wave_height * 1.5 * math.sin(self.animation_frame * 0.3 + i))
            else:
                wave_offset = int(wave_height * math.sin(self.animation_frame * 0.1 + i * 0.5))

            points = [
                (x_left, bottom),
                (x_left, bottom + wave_offset),
                (x_right, bottom + wave_offset),
                (x_right, bottom)
            ]

            pygame.draw.polygon(self.screen, color, points)

        # Draw ghost eyes
        eye_radius = radius * 0.3
        eye_offset_x = radius * 0.4
        eye_offset_y = -radius * 0.2 + bob_offset

        # White of eyes
        pygame.draw.circle(
            self.screen,
            WHITE,
            (center[0] - eye_offset_x, center[1] + eye_offset_y),
            eye_radius
        )
        pygame.draw.circle(
            self.screen,
            WHITE,
            (center[0] + eye_offset_x, center[1] + eye_offset_y),
            eye_radius
        )

        # Pupils that move based on animation frame
        pupil_radius = eye_radius * 0.5

        if scared:
            # Scared ghosts have X-shaped pupils
            pygame.draw.line(
                self.screen,
                BLACK,
                (center[0] - eye_offset_x - eye_radius * 0.5, center[1] + eye_offset_y - eye_radius * 0.5),
                (center[0] - eye_offset_x + eye_radius * 0.5, center[1] + eye_offset_y + eye_radius * 0.5),
                2
            )
            pygame.draw.line(
                self.screen,
                BLACK,
                (center[0] - eye_offset_x + eye_radius * 0.5, center[1] + eye_offset_y - eye_radius * 0.5),
                (center[0] - eye_offset_x - eye_radius * 0.5, center[1] + eye_offset_y + eye_radius * 0.5),
                2
            )
            pygame.draw.line(
                self.screen,
                BLACK,
                (center[0] + eye_offset_x - eye_radius * 0.5, center[1] + eye_offset_y - eye_radius * 0.5),
                (center[0] + eye_offset_x + eye_radius * 0.5, center[1] + eye_offset_y + eye_radius * 0.5),
                2
            )
            pygame.draw.line(
                self.screen,
                BLACK,
                (center[0] + eye_offset_x + eye_radius * 0.5, center[1] + eye_offset_y - eye_radius * 0.5),
                (center[0] + eye_offset_x - eye_radius * 0.5, center[1] + eye_offset_y + eye_radius * 0.5),
                2
            )
        else:
            # Normal pupils
            pupil_offset = eye_radius * 0.3 * math.sin(self.animation_frame * 0.1)

            pygame.draw.circle(
                self.screen,
                BLACK,
                (center[0] - eye_offset_x + pupil_offset, center[1] + eye_offset_y),
                pupil_radius
            )
            pygame.draw.circle(
                self.screen,
                BLACK,
                (center[0] + eye_offset_x + pupil_offset, center[1] + eye_offset_y),
                pupil_radius
            )

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

    def draw_info_panel(self, step=0, total_steps=0, action=None, walls_vanished=0, food_left=0,
                        ghost_scared=0, slow_motion=0, speed_boost=0):
        """Draw enhanced information panel at the bottom"""
        panel_rect = pygame.Rect(0, self.height - 60, self.width, 60)

        # Draw panel background
        pygame.draw.rect(self.screen, DARK_BLUE, panel_rect)
        pygame.draw.line(self.screen, WALL_BLUE, (0, self.height - 60), (self.width, self.height - 60), 2)

        if self.user_mode:
            # Draw information for user mode
            title = self.title_font.render(f"Pacman - User Control Mode", True, WHITE)
            self.screen.blit(title, (10, self.height - 55))

            # Score
            score_text = self.info_font.render(f"Score: {self.score}", True, YELLOW)
            self.screen.blit(score_text, (10, self.height - 30))

            # Lives
            lives_text = self.info_font.render(f"Lives: {self.lives}", True, RED)
            self.screen.blit(lives_text, (120, self.height - 30))

            # Food left
            food_info = self.info_font.render(f"Food: {food_left}", True, WHITE)
            self.screen.blit(food_info, (200, self.height - 30))

            # Wall status
            if walls_vanished > 0:
                status = f"Walls: {walls_vanished}"
                color = POWER_RED
            else:
                status = "Walls: Active"
                color = WALL_BLUE
            status_info = self.info_font.render(status, True, color)
            self.screen.blit(status_info, (290, self.height - 30))

            # Ghost status
            if ghost_scared > 0:
                ghost_status = f"Ghosts: Scared ({ghost_scared})"
                ghost_color = SCARED_GHOST
            else:
                ghost_status = "Ghosts: Normal"
                ghost_color = RED
            ghost_info = self.info_font.render(ghost_status, True, ghost_color)
            self.screen.blit(ghost_info, (400, self.height - 30))

            # Speed effects
            if slow_motion > 0:
                speed_status = f"Time: Slow ({slow_motion})"
                speed_color = SLOW_PILL_COLOR
            elif speed_boost > 0:
                speed_status = f"Speed: Boost ({speed_boost})"
                speed_color = SPEED_BOOST_COLOR
            else:
                speed_status = "Speed: Normal"
                speed_color = WHITE
            speed_info = self.info_font.render(speed_status, True, speed_color)
            self.screen.blit(speed_info, (580, self.height - 30))

            # Game controls help
            controls_text = self.small_font.render("Controls: Arrow Keys - Move, P - Pause, Q - Quit", True, WHITE)
            self.screen.blit(controls_text, (self.width - 350, self.height - 55))
        else:
            # Draw information text for A* mode
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

            # Ghost status if appropriate
            if ghost_scared > 0:
                ghost_info = self.info_font.render(f"Ghosts Scared: {ghost_scared}", True, SCARED_GHOST)
                self.screen.blit(ghost_info, (650, self.height - 30))

            # Speed effects if active
            if slow_motion > 0 or speed_boost > 0:
                if slow_motion > 0:
                    effect_text = f"Slow Motion: {slow_motion}"
                    effect_color = SLOW_PILL_COLOR
                else:
                    effect_text = f"Speed Boost: {speed_boost}"
                    effect_color = SPEED_BOOST_COLOR
                effect_info = self.info_font.render(effect_text, True, effect_color)
                self.screen.blit(effect_info, (self.width - 250, self.height - 55))

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
            elif particle.get('is_eye', False):
                # Ghost eye
                size = particle['size'] * (1 - progress * 0.2)
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

        # Update ghost eaten effects
        for effect in self.ghost_eaten_effects[:]:
            effect['elapsed'] += delta_time
            if effect['elapsed'] >= effect['lifetime']:
                self.ghost_eaten_effects.remove(effect)
                continue

            # Update position
            effect['y'] += effect['vy']

            # Update fade
            progress = effect['elapsed'] / effect['lifetime']
            alpha = int(255 * (1 - progress))

            # Make text bigger as it rises
            size_factor = 1.0 + progress * 0.5
            current_size = int(effect['size'] * size_factor)

            # Draw text
            font = pygame.font.SysFont('Arial', current_size, bold=True)
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

        # Update slow motion wave effect
        if self.slow_motion_wave:
            self.slow_motion_wave['elapsed'] += delta_time
            if self.slow_motion_wave['elapsed'] >= self.slow_motion_wave['lifetime']:
                self.slow_motion_wave = None
            else:
                # Update radius
                progress = self.slow_motion_wave['elapsed'] / self.slow_motion_wave['lifetime']
                radius = self.slow_motion_wave['max_radius'] * progress
                alpha = int(150 * (1 - progress))

                # Draw wave effect
                s = pygame.Surface((int(radius * 2), int(radius * 2)), pygame.SRCALPHA)
                color = (self.slow_motion_wave['color'][0], self.slow_motion_wave['color'][1],
                         self.slow_motion_wave['color'][2], alpha)
                pygame.draw.circle(s, color, (int(radius), int(radius)), int(radius),
                                   max(1, int(3 * (1 - progress))))
                self.screen.blit(s, (self.slow_motion_wave['x'] - radius, self.slow_motion_wave['y'] - radius))

                # Draw clock hands in the wave
                for i in range(5):
                    clock_radius = radius * 0.2
                    angle_offset = i * (360 / 5)
                    clock_x = self.slow_motion_wave['x'] + int(radius * 0.7 * math.cos(math.radians(angle_offset)))
                    clock_y = self.slow_motion_wave['y'] + int(radius * 0.7 * math.sin(math.radians(angle_offset)))

                    if 0 <= clock_x < self.width and 0 <= clock_y < self.height:
                        # Draw clock circle
                        pygame.draw.circle(s, (255, 255, 255, alpha),
                                           (int(clock_x - self.slow_motion_wave['x'] + radius),
                                            int(clock_y - self.slow_motion_wave['y'] + radius)),
                                           int(clock_radius))

                        # Draw clock hands
                        hand_angle = math.radians(self.animation_frame * 2 % 360)
                        hand_x = int(clock_radius * 0.8 * math.cos(hand_angle))
                        hand_y = int(clock_radius * 0.8 * math.sin(hand_angle))
                        pygame.draw.line(s, (0, 0, 0, alpha),
                                         (int(clock_x - self.slow_motion_wave['x'] + radius),
                                          int(clock_y - self.slow_motion_wave['y'] + radius)),
                                         (int(clock_x - self.slow_motion_wave['x'] + radius + hand_x),
                                          int(clock_y - self.slow_motion_wave['y'] + radius + hand_y)),
                                         2)

                self.screen.blit(s, (self.slow_motion_wave['x'] - radius, self.slow_motion_wave['y'] - radius))

        # Update speed boost wave effect
        if self.speed_boost_wave:
            self.speed_boost_wave['elapsed'] += delta_time
            if self.speed_boost_wave['elapsed'] >= self.speed_boost_wave['lifetime']:
                self.speed_boost_wave = None
            else:
                # Update radius
                progress = self.speed_boost_wave['elapsed'] / self.speed_boost_wave['lifetime']
                radius = self.speed_boost_wave['max_radius'] * progress
                alpha = int(150 * (1 - progress))

                # Draw wave effect
                s = pygame.Surface((int(radius * 2), int(radius * 2)), pygame.SRCALPHA)
                color = (self.speed_boost_wave['color'][0], self.speed_boost_wave['color'][1],
                         self.speed_boost_wave['color'][2], alpha)

                # Draw ripple
                pygame.draw.circle(s, color, (int(radius), int(radius)), int(radius),
                                   max(1, int(3 * (1 - progress))))

                # Draw lightning bolt shapes around the ripple
                for i in range(8):
                    angle = i * (360 / 8)
                    bolt_x = radius + int(radius * 0.7 * math.cos(math.radians(angle)))
                    bolt_y = radius + int(radius * 0.7 * math.sin(math.radians(angle)))

                    # Lightning bolt shape
                    bolt_size = radius * 0.2
                    bolt_points = [
                        (bolt_x, bolt_y - bolt_size),
                        (bolt_x - bolt_size * 0.5, bolt_y),
                        (bolt_x, bolt_y - bolt_size * 0.3),
                        (bolt_x + bolt_size * 0.5, bolt_y + bolt_size),
                        (bolt_x, bolt_y + bolt_size * 0.5),
                        (bolt_x - bolt_size * 0.3, bolt_y + bolt_size * 0.7)
                    ]

                    pygame.draw.polygon(s, (255, 255, 255, alpha), bolt_points)

                self.screen.blit(s, (self.speed_boost_wave['x'] - radius, self.speed_boost_wave['y'] - radius))

        # Update fruit particles
        for particle in self.fruit_particles[:]:
            particle['elapsed'] += delta_time
            if particle['elapsed'] >= particle['lifetime']:
                self.fruit_particles.remove(particle)
                continue

            # Update position
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['vy'] += 0.1  # Gravity effect

            # Update fade
            progress = particle['elapsed'] / particle['lifetime']
            particle['fade'] = int(255 * (1 - progress))

            # Draw fruit particle
            size = particle['size'] * (1 - progress * 0.3)
            s = pygame.Surface((max(1, int(size * 2)), max(1, int(size * 2))), pygame.SRCALPHA)
            pygame.draw.circle(s, (*particle['color'], particle['fade']),
                               (max(1, int(size)), max(1, int(size))), max(1, int(size)))
            self.screen.blit(s, (particle['x'] - size, particle['y'] - size))

    def draw_fruit(self, x: int, y: int):
        """Draw fruit bonus with animation"""
        center = self.cell_to_pixel(x, y)

        # Bouncing animation
        bounce_offset = int(3 * math.sin(self.animation_frame * 0.15))

        # Base fruit circle
        pygame.draw.circle(
            self.screen,
            FRUIT_COLOR,
            (center[0], center[1] + bounce_offset),
            self.cell_size // 3
        )

        # Highlight
        pygame.draw.circle(
            self.screen,
            (min(255, FRUIT_COLOR[0] + 50), min(255, FRUIT_COLOR[1] + 50), min(255, FRUIT_COLOR[2] + 50)),
            (center[0] - self.cell_size // 8, center[1] - self.cell_size // 8 + bounce_offset),
            self.cell_size // 8
        )

        # Stem
        pygame.draw.line(
            self.screen,
            (100, 150, 50),
            (center[0], center[1] - self.cell_size // 4 + bounce_offset),
            (center[0] + self.cell_size // 8, center[1] - self.cell_size // 2 + bounce_offset),
            2
        )

        # Leaf
        pygame.draw.ellipse(
            self.screen,
            (50, 180, 50),
            pygame.Rect(
                center[0] + self.cell_size // 12,
                center[1] - self.cell_size // 2 - self.cell_size // 12 + bounce_offset,
                self.cell_size // 6,
                self.cell_size // 8
            )
        )

        # Pulsing glow effect
        glow_radius = int(self.cell_size * 0.4 * (0.8 + 0.2 * math.sin(self.animation_frame * 0.1)))
        for i in range(3):
            s = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
            alpha = 50 - i * 15
            pygame.draw.circle(
                s,
                (*FRUIT_COLOR, alpha),
                (glow_radius, glow_radius),
                glow_radius - i * 2
            )
            self.screen.blit(s, (center[0] - glow_radius, center[1] - glow_radius + bounce_offset))

    def draw_teleport_pad(self, x: int, y: int):
        """Draw teleport pad with animation"""
        center = self.cell_to_pixel(x, y)
        radius = self.cell_size // 2 - 4

        # Base circle
        pygame.draw.circle(
            self.screen,
            TELEPORT_PAD_COLOR,
            center,
            radius
        )

        # Spinning portal effect
        angle = self.animation_frame % 360
        for i in range(4):
            a = math.radians(angle + i * 90)
            r = radius * 0.7
            end_x = center[0] + int(r * math.cos(a))
            end_y = center[1] + int(r * math.sin(a))
            pygame.draw.line(
                self.screen,
                (150, 255, 255),
                center,
                (end_x, end_y),
                2
            )

        # Ripple effect
        ripple_count = 3
        max_ripple = radius * 1.5
        for i in range(ripple_count):
            progress = (self.animation_frame * 0.05 + i/ripple_count) % 1.0
            ripple_radius = progress * max_ripple
            if ripple_radius <= max_ripple:
                s = pygame.Surface((int(ripple_radius * 2), int(ripple_radius * 2)), pygame.SRCALPHA)
                alpha = int(100 * (1 - progress))
                pygame.draw.circle(
                    s,
                    (*TELEPORT_PAD_COLOR, alpha),
                    (int(ripple_radius), int(ripple_radius)),
                    int(ripple_radius),
                    1
                )
                self.screen.blit(s, (center[0] - ripple_radius, center[1] - ripple_radius))

    def draw_slow_pill(self, x: int, y: int):
        """Draw slow motion pill with clock effect"""
        center = self.cell_to_pixel(x, y)
        radius = self.cell_size // 3

        # Base pill shape (elongated)
        pill_rect = pygame.Rect(
            center[0] - radius,
            center[1] - radius // 2,
            radius * 2,
            radius
        )
        pygame.draw.ellipse(
            self.screen,
            SLOW_PILL_COLOR,
            pill_rect
        )

        # Clock face in the middle
        clock_radius = radius // 2
        pygame.draw.circle(
            self.screen,
            WHITE,
            center,
            clock_radius
        )

        # Clock hands
        # Hour hand
        hour_angle = math.radians(self.animation_frame % 360)
        hour_x = center[0] + int(clock_radius * 0.5 * math.cos(hour_angle))
        hour_y = center[1] + int(clock_radius * 0.5 * math.sin(hour_angle))
        pygame.draw.line(
            self.screen,
            BLACK,
            center,
            (hour_x, hour_y),
            2
        )

        # Minute hand
        minute_angle = math.radians((self.animation_frame * 4) % 360)
        minute_x = center[0] + int(clock_radius * 0.7 * math.cos(minute_angle))
        minute_y = center[1] + int(clock_radius * 0.7 * math.sin(minute_angle))
        pygame.draw.line(
            self.screen,
            BLACK,
            center,
            (minute_x, minute_y),
            1
        )

        # Pulsing effect
        pulse_radius = int(radius * 1.2 * (0.8 + 0.2 * math.sin(self.animation_frame * 0.1)))
        s = pygame.Surface((pulse_radius * 2, pulse_radius), pygame.SRCALPHA)
        pygame.draw.ellipse(
            s,
            (*SLOW_PILL_COLOR, 50),
            pygame.Rect(0, 0, pulse_radius * 2, pulse_radius)
        )
        self.screen.blit(s, (center[0] - pulse_radius, center[1] - pulse_radius // 2))

    def draw_speed_boost(self, x: int, y: int):
        """Draw speed boost with lightning effect"""
        center = self.cell_to_pixel(x, y)

        # Lightning bolt shape
        bolt_points = [
            (center[0], center[1] - self.cell_size // 3),
            (center[0] - self.cell_size // 6, center[1]),
            (center[0], center[1] - self.cell_size // 12),
            (center[0] + self.cell_size // 6, center[1] + self.cell_size // 3),
            (center[0], center[1] + self.cell_size // 6),
            (center[0] - self.cell_size // 8, center[1] + self.cell_size // 4)
        ]

        # Flashing animation
        if self.animation_frame % 10 < 5:
            color = SPEED_BOOST_COLOR
        else:
            color = (min(255, SPEED_BOOST_COLOR[0] + 50),
                     min(255, SPEED_BOOST_COLOR[1] + 50),
                     min(255, SPEED_BOOST_COLOR[2] + 50))

        # Draw lightning bolt
        pygame.draw.polygon(
            self.screen,
            color,
            bolt_points
        )

        # Glow effect
        s = pygame.Surface((self.cell_size, self.cell_size), pygame.SRCALPHA)
        pygame.draw.polygon(
            s,
            (*color, 100),
            [(p[0] - center[0] + self.cell_size // 2,
              p[1] - center[1] + self.cell_size // 2) for p in bolt_points]
        )
        self.screen.blit(s, (center[0] - self.cell_size // 2, center[1] - self.cell_size // 2))

        # Small speed lines
        for _ in range(2):
            start_x = center[0] - random.randint(-self.cell_size // 4, self.cell_size // 4)
            start_y = center[1] - random.randint(-self.cell_size // 4, self.cell_size // 4)

            line_length = random.randint(3, 6)
            angle = random.uniform(0, 2 * math.pi)

            end_x = start_x + int(line_length * math.cos(angle))
            end_y = start_y + int(line_length * math.sin(angle))

            pygame.draw.line(
                self.screen,
                WHITE,
                (start_x, start_y),
                (end_x, end_y),
                1
            )

    def draw_maze(self, pacman_pos, remaining_food, remaining_magical_pies,
                  walls_vanished_steps, action=None, step=0, total_steps=0, ghost_positions=None,
                  ghost_scared_steps=0, slow_motion_steps=0, speed_boost_steps=0,
                  remaining_fruits=None, remaining_slow_pills=None, remaining_speed_boosts=None,
                  teleport_pads=None, moving_walls_active=True):
        """Draw the current state of the maze with enhanced visuals and all game mechanics"""
        # Store current state for effects
        self.walls_vanished = walls_vanished_steps
        self.ghosts_scared = ghost_scared_steps > 0
        self.slow_motion_active = slow_motion_steps > 0
        self.speed_boost_active = speed_boost_steps > 0
        self.moving_walls_active = moving_walls_active

        # Fill the screen with background
        self.screen.fill(BLACK)

        # Apply time distortion effect for slow motion
        if self.slow_motion_active:
            # Matrix-like time distortion effect
            for i in range(10):
                x = random.randint(0, self.width)
                y = random.randint(0, self.height - 60)
                length = random.randint(5, 20)
                speed = random.uniform(0.5, 2.0)
                color = (0, 200, 255)
                self.matrix_effect.append({
                    'x': x,
                    'y': y,
                    'length': length,
                    'speed': speed,
                    'color': color,
                    'alpha': random.randint(50, 150)
                })

            # Draw matrix effect
            for effect in self.matrix_effect[:]:
                s = pygame.Surface((2, effect['length']), pygame.SRCALPHA)
                s.fill((*effect['color'], effect['alpha']))
                self.screen.blit(s, (effect['x'], effect['y']))

                # Move effect down
                effect['y'] += effect['speed']
                effect['alpha'] -= 1

                if effect['y'] > self.height or effect['alpha'] <= 0:
                    self.matrix_effect.remove(effect)

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
                # Draw regular walls
                if self.maze.is_wall(x, y):
                    is_moving_wall = (x, y) in self.maze.moving_walls
                    self.draw_wall(x, y, walls_vanished_steps > 0, is_moving_wall, moving_walls_active)

                # Draw corners
                if self.maze.is_corner(x, y):
                    self.draw_corner(x, y)

                # Draw teleport pads
                if teleport_pads and (x, y) in teleport_pads:
                    self.draw_teleport_pad(x, y)

        # Draw food points with enhanced visuals
        for x, y in remaining_food:
            self.draw_food(x, y)

        # Draw magical pies with enhanced visuals
        for x, y in remaining_magical_pies:
            self.draw_magical_pie(x, y)

        # Draw fruits
        if remaining_fruits:
            for x, y in remaining_fruits:
                self.draw_fruit(x, y)

        # Draw slow pills
        if remaining_slow_pills:
            for x, y in remaining_slow_pills:
                self.draw_slow_pill(x, y)

        # Draw speed boosts
        if remaining_speed_boosts:
            for x, y in remaining_speed_boosts:
                self.draw_speed_boost(x, y)

        # Draw ghosts
        if ghost_positions:
            for i, ghost_pos in enumerate(ghost_positions):
                self.draw_ghost(*ghost_pos, i, ghost_scared_steps > 0)

        # Draw Pacman with animation
        pacman_x, pacman_y = pacman_pos
        self.draw_pacman(pacman_x, pacman_y, walls_vanished_steps, action)

        # Add speed lines for speed boost
        if speed_boost_steps > 0:
            angle = 0
            if action == 'North':
                angle = 270
            elif action == 'East':
                angle = 0
            elif action == 'South':
                angle = 90
            elif action == 'West':
                angle = 180

            # Create speed lines behind pacman
            if action and action != 'Stop':
                center = self.cell_to_pixel(pacman_x, pacman_y)
                opposite_angle = (angle + 180) % 360

                for _ in range(3):
                    # Random angle variation
                    line_angle = math.radians(opposite_angle + random.randint(-30, 30))
                    line_length = random.randint(10, 25)

                    start_x = center[0]
                    start_y = center[1]
                    end_x = start_x + int(line_length * math.cos(line_angle))
                    end_y = start_y + int(line_length * math.sin(line_angle))

                    self.speed_lines.append({
                        'start': (start_x, start_y),
                        'end': (end_x, end_y),
                        'width': random.randint(1, 3),
                        'color': (255, 100, 100, 150),
                        'lifetime': random.uniform(0.2, 0.5),
                        'elapsed': 0
                    })

            # Draw speed lines
            for line in self.speed_lines[:]:
                line['elapsed'] += 0.05
                if line['elapsed'] >= line['lifetime']:
                    self.speed_lines.remove(line)
                    continue

                progress = line['elapsed'] / line['lifetime']
                alpha = int(150 * (1 - progress))

                s = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                pygame.draw.line(
                    s,
                    (*line['color'][:3], alpha),
                    line['start'],
                    line['end'],
                    line['width']
                )
                self.screen.blit(s, (0, 0))

        # Draw all particle effects
        self.update_particles(min(0.05, self.step_delay / 3))

        # Draw info panel with all status variables
        self.draw_info_panel(
            step, total_steps, action, walls_vanished_steps, len(remaining_food),
            ghost_scared_steps, slow_motion_steps, speed_boost_steps
        )

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

    def user_play_game(self):
        """User-controlled game mode"""
        if not self.user_mode:
            print("Error: Visualizer not initialized in user mode")
            return

        if self.logger: self.logger.info("Starting user-controlled game")

        # Initialize game state with all new mechanics
        pacman_pos = self.maze.pacman_start
        remaining_food = set(self.maze.food_points)
        remaining_magical_pies = set(self.maze.magical_pies)
        walls_vanished_steps = 0
        ghost_positions = list(self.maze.ghost_starts)  # Start with 2 ghosts from maze

        # New mechanics
        remaining_fruits = set()
        remaining_slow_pills = set(self.maze.slow_pills)
        remaining_speed_boosts = set(self.maze.speed_boosts)
        ghost_scared_steps = 0
        slow_motion_steps = 0
        speed_boost_steps = 0
        moving_walls_active = True
        teleport_pads = self.maze.teleport_pads

        # Draw initial state with all new elements
        self.draw_maze(pacman_pos, remaining_food, remaining_magical_pies,
                       walls_vanished_steps, None, 0, 0, ghost_positions,
                       ghost_scared_steps, slow_motion_steps, speed_boost_steps,
                       remaining_fruits, remaining_slow_pills, remaining_speed_boosts,
                       teleport_pads, moving_walls_active)

        # Print instructions
        print("User control mode: Use arrow keys to move Pacman.")
        print("P to pause, Q to quit.")

        if self.logger: self.logger.info("User game started")

        # Game variables
        clock = pygame.time.Clock()
        game_over = False
        win = False
        current_action = None
        last_ghost_move_time = time.time()
        ghost_move_interval = 0.5  # Base ghost movement interval
        fruit_spawn_timer = 0
        fruit_spawn_interval = 15  # Spawn fruit every 15 seconds
        last_wall_toggle_time = time.time()
        wall_toggle_interval = 10  # Toggle moving walls every 10 seconds

        # Game loop
        running = True
        while running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.KEYDOWN:
                    # Game control keys
                    if event.key == pygame.K_q:
                        running = False
                    elif event.key == pygame.K_p:
                        self.paused = not self.paused
                        if self.logger:
                            self.logger.info("Game paused" if self.paused else "Game resumed")

                    # Movement keys (only if not paused or game over)
                    if not self.paused and not game_over:
                        x, y = pacman_pos
                        new_pos = pacman_pos

                        if event.key == pygame.K_UP:
                            new_pos = (x, y - 1)
                            current_action = 'North'
                        elif event.key == pygame.K_RIGHT:
                            new_pos = (x + 1, y)
                            current_action = 'East'
                        elif event.key == pygame.K_DOWN:
                            new_pos = (x, y + 1)
                            current_action = 'South'
                        elif event.key == pygame.K_LEFT:
                            new_pos = (x - 1, y)
                            current_action = 'West'

                        # Check if move is valid (not into a wall)
                        if (not self.maze.is_wall(*new_pos, moving_walls_active) or walls_vanished_steps > 0):
                            # Update position
                            pacman_pos = new_pos

                            # Create speed lines when speed boost is active
                            if speed_boost_steps > 0 and current_action != 'Stop':
                                center = self.cell_to_pixel(*pacman_pos)
                                for _ in range(3):
                                    angle = 0
                                    if current_action == 'North':
                                        angle = math.radians(270)
                                    elif current_action == 'East':
                                        angle = math.radians(180)
                                    elif current_action == 'South':
                                        angle = math.radians(90)
                                    elif current_action == 'West':
                                        angle = math.radians(0)

                                    angle += math.radians(random.randint(-20, 20))
                                    length = random.randint(15, 25)
                                    start_x = center[0]
                                    start_y = center[1]
                                    end_x = start_x + int(length * math.cos(angle))
                                    end_y = start_y + int(length * math.sin(angle))

                                    self.speed_lines.append({
                                        'start': (start_x, start_y),
                                        'end': (end_x, end_y),
                                        'width': random.randint(1, 3),
                                        'color': (255, 100, 100, 150),
                                        'lifetime': random.uniform(0.2, 0.5),
                                        'elapsed': 0
                                    })

                            # Handle teleport pads
                            teleport_dest = teleport_pads.get(pacman_pos, None)
                            if teleport_dest:
                                # Create teleport effect
                                self.create_teleport_effect(pacman_pos, teleport_dest)

                                # Update position
                                pacman_pos = teleport_dest

                                # Play sound
                                if self.sounds_loaded:
                                    self.teleport_sound.play()

                                if self.logger:
                                    self.logger.info(f"Teleported from {new_pos} to {teleport_dest}")

                            # Handle wall vanishing duration
                            if walls_vanished_steps > 0:
                                walls_vanished_steps -= 1

                            # Handle ghost scared duration
                            if ghost_scared_steps > 0:
                                ghost_scared_steps -= 1

                            # Handle slow motion duration
                            if slow_motion_steps > 0:
                                slow_motion_steps -= 1

                            # Handle speed boost duration
                            if speed_boost_steps > 0:
                                speed_boost_steps -= 1

                            # Handle corner teleportation
                            if self.maze.is_corner(*pacman_pos):
                                teleport_pos = self.maze.get_opposite_corner(*pacman_pos)
                                if teleport_pos and teleport_pos != pacman_pos:
                                    if self.logger:
                                        self.logger.info(f"Teleportation from {pacman_pos} to {teleport_pos}")

                                    # Create teleport effect
                                    self.create_teleport_effect(pacman_pos, teleport_pos)

                                    # Update position
                                    pacman_pos = teleport_pos

                                    # Play sound
                                    if self.sounds_loaded:
                                        self.teleport_sound.play()

                            # Handle food collection
                            if pacman_pos in remaining_food:
                                if self.logger:
                                    self.logger.info(f"Food eaten at {pacman_pos}")

                                # Create particles
                                self.create_food_particles(*pacman_pos)

                                # Remove food and update score
                                remaining_food.remove(pacman_pos)
                                self.score += 10

                                # Play sound
                                if self.sounds_loaded:
                                    self.eat_sound.play()

                            # Handle magical pie effects
                            if pacman_pos in remaining_magical_pies:
                                if self.logger:
                                    self.logger.info(f"Magical pie eaten at {pacman_pos}")

                                # Create particles
                                self.create_power_particles(*pacman_pos)

                                # Remove pie and update wall status
                                remaining_magical_pies.remove(pacman_pos)
                                walls_vanished_steps = 5
                                ghost_scared_steps = 15
                                self.score += 50

                                # Play sound
                                if self.sounds_loaded:
                                    self.power_sound.play()

                            # Handle fruit collection
                            if pacman_pos in remaining_fruits:
                                if self.logger:
                                    self.logger.info(f"Fruit eaten at {pacman_pos}")

                                # Create fruit particles
                                for _ in range(20):
                                    angle = random.uniform(0, 2 * math.pi)
                                    speed = random.uniform(1, 4)
                                    size = random.uniform(2, 5)
                                    lifetime = random.uniform(0.5, 1.5)
                                    center = self.cell_to_pixel(*pacman_pos)
                                    self.fruit_particles.append({
                                        'x': center[0],
                                        'y': center[1],
                                        'vx': math.cos(angle) * speed,
                                        'vy': math.sin(angle) * speed,
                                        'size': size,
                                        'color': FRUIT_COLOR,
                                        'fade': 255,
                                        'lifetime': lifetime,
                                        'elapsed': 0
                                    })

                                # Remove fruit and update score
                                remaining_fruits.remove(pacman_pos)
                                self.score += 100

                                # Play sound
                                if self.sounds_loaded and hasattr(self, 'fruit_sound'):
                                    self.fruit_sound.play()

                            # Handle slow pill collection
                            if pacman_pos in remaining_slow_pills:
                                if self.logger:
                                    self.logger.info(f"Slow pill eaten at {pacman_pos}")

                                # Create slow motion effect
                                center = self.cell_to_pixel(*pacman_pos)
                                self.slow_motion_wave = {
                                    'x': center[0],
                                    'y': center[1],
                                    'radius': 0,
                                    'max_radius': self.cell_size * 10,
                                    'color': SLOW_PILL_COLOR,
                                    'lifetime': 1.0,
                                    'elapsed': 0
                                }

                                # Remove pill and activate slow motion
                                remaining_slow_pills.remove(pacman_pos)
                                slow_motion_steps = 15
                                self.score += 30

                                # Play sound
                                if self.sounds_loaded and hasattr(self, 'slow_motion_sound'):
                                    self.slow_motion_sound.play()

                            # Handle speed boost collection
                            if pacman_pos in remaining_speed_boosts:
                                if self.logger:
                                    self.logger.info(f"Speed boost eaten at {pacman_pos}")

                                # Create speed boost effect
                                center = self.cell_to_pixel(*pacman_pos)
                                self.speed_boost_wave = {
                                    'x': center[0],
                                    'y': center[1],
                                    'radius': 0,
                                    'max_radius': self.cell_size * 8,
                                    'color': SPEED_BOOST_COLOR,
                                    'lifetime': 1.0,
                                    'elapsed': 0
                                }

                                # Remove boost and activate speed boost
                                remaining_speed_boosts.remove(pacman_pos)
                                speed_boost_steps = 10
                                self.score += 30

                                # Play sound
                                if self.sounds_loaded and hasattr(self, 'speed_boost_sound'):
                                    self.speed_boost_sound.play()

                            # Check win condition
                            if not remaining_food:
                                win = True
                                game_over = True
                                if self.logger:
                                    self.logger.info("Player won - all food collected")

            # Skip updates if paused
            if self.paused:
                # Draw pause message
                s = pygame.Surface((self.width, 80))
                s.set_alpha(200)
                s.fill(BLACK)
                self.screen.blit(s, (0, self.height // 2 - 40))

                text = self.title_font.render("GAME PAUSED", True, WHITE)
                text_rect = text.get_rect(center=(self.width // 2, self.height // 2))
                self.screen.blit(text, text_rect)

                pygame.display.flip()
                clock.tick(30)
                continue

            # Skip updates if game over
            if game_over:
                # Draw game over message
                s = pygame.Surface((self.width, 80))
                s.set_alpha(200)
                s.fill(BLACK)
                self.screen.blit(s, (0, self.height // 2 - 40))

                if win:
                    text = self.title_font.render(f"YOU WIN! Score: {self.score}", True, GREEN)
                else:
                    text = self.title_font.render(f"GAME OVER! Score: {self.score}", True, RED)

                text_rect = text.get_rect(center=(self.width // 2, self.height // 2))
                self.screen.blit(text, text_rect)

                exit_text = self.info_font.render("Press Q to quit", True, WHITE)
                exit_rect = exit_text.get_rect(center=(self.width // 2, self.height // 2 + 30))
                self.screen.blit(exit_text, exit_rect)

                pygame.display.flip()
                clock.tick(30)
                continue

            # Fruit spawn logic
            current_time = time.time()
            fruit_spawn_timer += clock.get_time() / 1000  # Convert to seconds

            if fruit_spawn_timer >= fruit_spawn_interval and len(remaining_fruits) < 2:
                # Spawn a new fruit at a random position where there's not already a fruit
                possible_positions = []
                for y in range(self.maze.height):
                    for x in range(self.maze.width):
                        pos = (x, y)
                        if (not self.maze.is_wall(*pos, moving_walls_active) and
                                pos != pacman_pos and
                                pos not in remaining_fruits and
                                pos not in ghost_positions):
                            possible_positions.append(pos)

                if possible_positions:
                    new_fruit_pos = random.choice(possible_positions)
                    remaining_fruits.add(new_fruit_pos)
                    if self.logger:
                        self.logger.info(f"Fruit spawned at {new_fruit_pos}")

                fruit_spawn_timer = 0

            # Toggle moving walls periodically
            if current_time - last_wall_toggle_time >= wall_toggle_interval and self.maze.moving_walls:
                moving_walls_active = not moving_walls_active
                last_wall_toggle_time = current_time
                if self.logger:
                    self.logger.info(f"Moving walls toggled to {'active' if moving_walls_active else 'inactive'}")

            # Move ghosts at fixed intervals, adjusted by slow motion
            effective_ghost_interval = ghost_move_interval
            if slow_motion_steps > 0:
                effective_ghost_interval = ghost_move_interval * 2  # Ghosts move at half speed

            if current_time - last_ghost_move_time >= effective_ghost_interval:
                # Move ghosts - behavior depends on scared state
                for i, ghost_pos in enumerate(ghost_positions):
                    x, y = ghost_pos
                    valid_moves = []

                    for dx, dy in [(0, -1), (1, 0), (0, 1), (-1, 0)]:  # North, East, South, West
                        nx, ny = x + dx, y + dy
                        if not self.maze.is_wall(nx, ny, moving_walls_active):
                            valid_moves.append((nx, ny))

                    if not valid_moves:
                        continue

                    # Different movement logic when ghosts are scared
                    if ghost_scared_steps > 0:
                        # Calculate distance to Pacman for each move
                        move_distances = []
                        for move in valid_moves:
                            dist = abs(move[0] - pacman_pos[0]) + abs(move[1] - pacman_pos[1])
                            move_distances.append((move, dist))

                        # Find moves that maximize distance from Pacman
                        move_distances.sort(key=lambda x: -x[1])  # Sort by descending distance
                        best_distance = move_distances[0][1]
                        best_moves = [m for m, d in move_distances if d == best_distance]

                        # Choose randomly from the best moves
                        new_pos = random.choice(best_moves)
                    else:
                        # Normal movement - chase Pacman with 60% probability
                        if random.random() < 0.6:
                            # Calculate distance to Pacman for each move
                            move_distances = []
                            for move in valid_moves:
                                dist = abs(move[0] - pacman_pos[0]) + abs(move[1] - pacman_pos[1])
                                move_distances.append((move, dist))

                            # Find moves that minimize distance to Pacman
                            move_distances.sort(key=lambda x: x[1])  # Sort by ascending distance
                            best_distance = move_distances[0][1]
                            best_moves = [m for m, d in move_distances if d == best_distance]

                            # Choose randomly from the best moves
                            new_pos = random.choice(best_moves)
                        else:
                            # Random movement
                            new_pos = random.choice(valid_moves)

                    ghost_positions[i] = new_pos

                last_ghost_move_time = current_time

                # If speed boost is active, Pacman gets an extra move for each ghost move
                if speed_boost_steps > 0 and not game_over:
                    # We don't actually move Pacman automatically, but we can reduce the speed boost counter
                    # to reflect the "extra" move that Pacman gets
                    speed_boost_steps = max(0, speed_boost_steps - 1)

            # Check ghost collision
            if pacman_pos in ghost_positions:
                collision_index = ghost_positions.index(pacman_pos)

                if ghost_scared_steps > 0:
                    # Eat the ghost
                    if self.logger:
                        self.logger.info(f"Ghost {collision_index} eaten")

                    # Create ghost eaten effect
                    center = self.cell_to_pixel(*pacman_pos)
                    self.ghost_eaten_effects.append({
                        'x': center[0],
                        'y': center[1],
                        'text': '200',
                        'color': BLUE,
                        'size': 20,
                        'vy': -1.5,
                        'lifetime': 1.0,
                        'elapsed': 0
                    })

                    # Remove ghost and add score
                    ghost_positions.pop(collision_index)
                    self.score += 200

                    # Play sound
                    if self.sounds_loaded and hasattr(self, 'ghost_eat_sound'):
                        self.ghost_eat_sound.play()

                    # Respawn ghost after a delay (5 seconds)
                    # For this demo, we'll just add it back at a random valid position
                    spawn_timer = current_time + 5

                    # This would need to be handled in a separate data structure for multiple ghosts
                    # For now, immediately respawn at a random position far from Pacman
                    possible_positions = []
                    min_distance = 5  # Minimum Manhattan distance from Pacman

                    for y in range(self.maze.height):
                        for x in range(self.maze.width):
                            pos = (x, y)
                            distance = abs(x - pacman_pos[0]) + abs(y - pacman_pos[1])
                            if (not self.maze.is_wall(*pos, moving_walls_active) and
                                    distance >= min_distance and
                                    pos not in ghost_positions):
                                possible_positions.append(pos)

                    if possible_positions:
                        ghost_positions.append(random.choice(possible_positions))
                else:
                    # Ghost caught Pacman
                    if self.logger: self.logger.info("Pacman caught by ghost")

                    # Play death sound
                    if self.sounds_loaded and hasattr(self, 'death_sound'):
                        self.death_sound.play()

                    # Lose a life
                    self.lives -= 1

                    if self.lives <= 0:
                        # Game over
                        game_over = True
                        if self.logger: self.logger.info("Game over - no lives left")
                    else:
                        # Reset positions
                        pacman_pos = self.maze.pacman_start
                        ghost_positions = list(self.maze.ghost_starts)
                        if self.logger: self.logger.info(f"Life lost - {self.lives} remaining")

            # Update display with all game elements
            self.draw_maze(pacman_pos, remaining_food, remaining_magical_pies,
                           walls_vanished_steps, current_action, 0, 0, ghost_positions,
                           ghost_scared_steps, slow_motion_steps, speed_boost_steps,
                           remaining_fruits, remaining_slow_pills, remaining_speed_boosts,
                           teleport_pads, moving_walls_active)

            # Cap framerate
            clock.tick(30)

        if self.logger: self.logger.info("User game ended")
        pygame.quit()

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
        ghost_positions = list(self.maze.ghost_starts)  # Initialize ghosts

        # Draw initial state
        self.draw_maze(pacman_pos, remaining_food, remaining_magical_pies,
                       walls_vanished_steps, None, 0, len(actions), ghost_positions)

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
        last_ghost_move = time.time()
        ghost_move_interval = 0.5  # Move ghosts every half second

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

            # Move ghosts occasionally
            current_time = time.time()
            if current_time - last_ghost_move >= ghost_move_interval:
                # Move ghosts randomly
                for i, ghost_pos in enumerate(ghost_positions):
                    x, y = ghost_pos
                    valid_moves = []
                    for dx, dy in [(0, -1), (1, 0), (0, 1), (-1, 0)]:
                        nx, ny = x + dx, y + dy
                        if not self.maze.is_wall(nx, ny):
                            valid_moves.append((nx, ny))
                    if valid_moves:
                        ghost_positions[i] = random.choice(valid_moves)
                last_ghost_move = current_time

            # Check ghost collision
            if pacman_pos in ghost_positions:
                game_over = True
                if self.logger: self.logger.warning("Pacman caught by ghost!")
                if self.sounds_loaded and hasattr(self, 'death_sound'):
                    self.death_sound.play()
                break

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
                               walls_vanished_steps, action, step, len(actions), ghost_positions)

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
                           walls_vanished_steps, action, step, len(actions), ghost_positions)

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
            if pacman_pos in ghost_positions:
                completion_text = "GAME OVER: Pacman caught by ghost!"
            else:
                completion_text = "GAME OVER: Pacman got stuck in a wall!"
            text_color = POWER_RED
            if self.logger: self.logger.warning(completion_text)
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

def create_ghost_eaten_effect(self, x, y, ghost_index=0):
    """Create effects for eating a ghost"""
    center = self.cell_to_pixel(x, y)
    color = GHOST_COLORS[ghost_index % len(GHOST_COLORS)]

    # Add score pop-up
    self.ghost_eaten_effects.append({
        'x': center[0],
        'y': center[1],
        'text': '+200',
        'color': color,
        'size': 24,
        'vy': -2,
        'lifetime': 1.2,
        'elapsed': 0
    })

    # Add ghost dissolve particles
    for _ in range(30):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(2, 6)
        size = random.uniform(3, 8)
        lifetime = random.uniform(0.8, 2.0)
        self.particles.append({
            'x': center[0],
            'y': center[1],
            'vx': math.cos(angle) * speed,
            'vy': math.sin(angle) * speed,
            'size': size,
            'color': color,
            'fade': 230,
            'lifetime': lifetime,
            'elapsed': 0
        })

    # Add ghost eyes "running away" effect
    eye_spacing = self.cell_size // 3
    left_eye_pos = (center[0] - eye_spacing // 2, center[1])
    right_eye_pos = (center[0] + eye_spacing // 2, center[1])

    # Random direction for eyes to flee
    flee_angle = random.uniform(0, 2 * math.pi)

    for eye_pos in [left_eye_pos, right_eye_pos]:
        # White of eye
        self.particles.append({
            'x': eye_pos[0],
            'y': eye_pos[1],
            'vx': math.cos(flee_angle) * 3,
            'vy': math.sin(flee_angle) * 3,
            'size': self.cell_size // 6,
            'color': WHITE,
            'fade': 255,
            'lifetime': 1.0,
            'elapsed': 0,
            'is_eye': True
        })

        # Pupil
        self.particles.append({
            'x': eye_pos[0],
            'y': eye_pos[1],
            'vx': math.cos(flee_angle) * 3,
            'vy': math.sin(flee_angle) * 3,
            'size': self.cell_size // 12,
            'color': BLACK,
            'fade': 255,
            'lifetime': 1.0,
            'elapsed': 0,
            'is_eye': True
        })