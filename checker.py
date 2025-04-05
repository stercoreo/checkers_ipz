import pygame
import math

class Checker:
    """Represents a game piece with synchronized visual styling."""

    def __init__(self, color, row, col, cell_size, colors):
        """
        Initialize checker with shared color scheme.
        
        Args:
            color (str): 'white' or 'black'
            row (int): Starting row
            col (int): Starting column
            cell_size (int): Size of board cells
            colors (dict): Shared color dictionary
        """
        self.color = color
        self.row = row
        self.col = col
        self.cell_size = cell_size
        self.colors = colors
        self.x = col * cell_size + cell_size // 2
        self.y = row * cell_size + cell_size // 2
        self.target_x = self.x
        self.target_y = self.y
        self.is_king = False
        self.animation_speed = 0.3
        self.is_capturing = False

    def update(self):
        """
        Update position during animation.
        
        Returns:
            bool: True if still animating, False if complete
        """
        if self.x == self.target_x and self.y == self.target_y:
            return False
            
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        self.x += dx * self.animation_speed
        self.y += dy * self.animation_speed
        
        if abs(dx) < 1 and abs(dy) < 1:
            self.x = self.target_x
            self.y = self.target_y
            
        return True

    def move_to(self, row, col):
        """
        Set target position for movement.
        
        Args:
            row (int): Target row
            col (int): Target column
        """
        self.row = row
        self.col = col
        self.target_x = col * self.cell_size + self.cell_size // 2
        self.target_y = row * self.cell_size + self.cell_size // 2

    def draw(self, screen):
        """Render checker with consistent visual style."""
        # Draw shadow (except during capture)
        if not self.is_capturing:
            shadow = pygame.Surface((self.cell_size, self.cell_size), pygame.SRCALPHA)
            pygame.draw.circle(shadow, self.colors["text_shadow"] + (150,),
                             (self.cell_size//2 + 3, self.cell_size//2 + 3),
                             self.cell_size//2 - 10)
            screen.blit(shadow, (self.col * self.cell_size, self.row * self.cell_size))
        
        # Draw body
        body_color = self.colors["light"] if self.color == 'white' else self.colors["dark"]
        pygame.draw.circle(screen, body_color,
                         (self.x, self.y),
                         self.cell_size//2 - 10)
        
        # Draw border
        border_color = self.colors["text"] if self.color == 'white' else self.colors["background"]
        pygame.draw.circle(screen, border_color,
                         (self.x, self.y),
                         self.cell_size//2 - 10, 2)
        
        # Draw king crown
        if self.is_king:
            self._draw_king(screen)

    def _draw_king(self, screen):
        """Render king decoration with accent color."""
        # Base crown
        pygame.draw.circle(screen, self.colors["highlight"],
                         (self.x, self.y),
                         self.cell_size//4)
        
        # Crown points
        points = []
        for i in range(5):
            angle = math.pi/2 - i * 2 * math.pi/5
            outer_x = self.x + math.cos(angle) * self.cell_size//4
            outer_y = self.y - math.sin(angle) * self.cell_size//4
            inner_x = self.x + math.cos(angle + math.pi/5) * self.cell_size//8
            inner_y = self.y - math.sin(angle + math.pi/5) * self.cell_size//8
            points.extend([(outer_x, outer_y), (inner_x, inner_y)])
        
        # Detailed crown
        pygame.draw.polygon(screen, self.colors["highlight"], points)
        pygame.draw.polygon(screen, self.colors["button_border"], points, 2)