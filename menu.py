import pygame
import random
from ai import AIPlayer

class Menu:
    """Handles the main menu interface and user interactions."""
    
    def __init__(self, width, height):
        """
        Initialize menu components and visual properties.
        
        Args:
            width (int): Screen width in pixels
            height (int): Screen height in pixels
        """
        self.width = width
        self.height = height
        
        # Menu button configurations
        self.buttons = [
            
            {"text": " AI - Easy", "action": "ai_easy", "difficulty": AIPlayer.DIFFICULTY_EASY},
            {"text": " AI - Medium", "action": "ai_medium", "difficulty": AIPlayer.DIFFICULTY_MEDIUM},
            {"text": " AI - Hard", "action": "ai_hard", "difficulty": AIPlayer.DIFFICULTY_HARD},
            {"text": "Quit", "action": "quit"}
        ]
        
        # Font setup for UI elements
        self.title_font = pygame.font.Font(None, 72)
        self.button_font = pygame.font.Font(None, 36)
        self.subtitle_font = pygame.font.Font(None, 24)
        
        # Color scheme for UI components
        self.colors = {
            "background": (30, 30, 40),
            "title": (220, 200, 180),
            "subtitle": (180, 170, 160),
            "button_normal": (70, 70, 90),
            "button_hover": (100, 100, 120),
            "button_text": (220, 210, 190),
            "button_border": (150, 140, 130),
            "highlight": (180, 150, 100)
        }
        
        self.background = self._create_textured_background()
        self._init_buttons()

    def _create_textured_background(self):
        """Generate a textured background surface."""
        background = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        background.fill(self.colors["background"])
        
        # Add subtle noise texture
        for _ in range(20000):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            alpha = random.randint(5, 15)
            color = random.randint(20, 40), random.randint(20, 40), random.randint(25, 45), alpha
            pygame.draw.circle(background, color, (x, y), 1)
        
        return background

    def _init_buttons(self):
        """Initialize button geometry and visual properties."""
        button_width = 350
        button_height = 60
        start_y = self.height // 2 - 120
        
        for i, button in enumerate(self.buttons):
            x = self.width // 2 - button_width // 2
            y = start_y + i * (button_height + 12)
            
            button.update({
                "rect": pygame.Rect(x, y, button_width, button_height),
                "hover": False,
                "border_width": 2,
                "corner_radius": 4
            })

    def draw(self, screen):
        """Render all menu components."""
        screen.blit(self.background, (0, 0))
        
        # Render title text with shadow
        title_shadow = self.title_font.render("CHECKERS", True, (20, 20, 20))
        screen.blit(title_shadow, (self.width//2 - title_shadow.get_width()//2 + 3, 83))
        
        title = self.title_font.render("CHECKERS", True, self.colors["title"])
        screen.blit(title, (self.width//2 - title.get_width()//2, 80))
        
        # Render subtitle
        subtitle = self.subtitle_font.render("Classic Board Game", True, self.colors["subtitle"])
        screen.blit(subtitle, (self.width//2 - subtitle.get_width()//2, 160))
        
        # Render interactive buttons
        for button in self.buttons:
            self._draw_button(screen, button)

    def _draw_button(self, screen, button):
        """Render an individual menu button."""
        # Button background
        color = self.colors["button_hover"] if button["hover"] else self.colors["button_normal"]
        rect = button["rect"]
        pygame.draw.rect(screen, color, rect, border_radius=button["corner_radius"])
        
        # Button border
        border_color = self.colors["highlight"] if button["hover"] else self.colors["button_border"]
        pygame.draw.rect(screen, border_color, rect, button["border_width"], button["corner_radius"])
        
        # Button text with shadow
        text_color = self.colors["highlight"] if button["hover"] else self.colors["button_text"]
        text_shadow = self.button_font.render(button["text"], True, (20, 20, 20))
        screen.blit(text_shadow, (rect.centerx - text_shadow.get_width()//2 + 2, rect.centery - text_shadow.get_height()//2 + 2))
        
        text = self.button_font.render(button["text"], True, text_color)
        screen.blit(text, (rect.centerx - text.get_width()//2, rect.centery - text.get_height()//2))
        
        # Hover indicator
        if button["hover"]:
            self._draw_hover_indicator(screen, rect)

    def _draw_hover_indicator(self, screen, rect):
        """Draw visual feedback for button hover state."""
        line_y = rect.bottom - 5
        pygame.draw.line(
            screen, self.colors["highlight"],
            (rect.left + 15, line_y), (rect.right - 15, line_y),
            2
        )

    def handle_click(self, pos):
        """
        Process mouse click events on menu buttons.
        
        Args:
            pos (tuple): Mouse coordinates (x, y)
            
        Returns:
            str: Action associated with clicked button or None
        """
        for button in self.buttons:
            if button["rect"].collidepoint(pos):
                return button["action"]
        return None

    def update_hover(self, pos):
        """
        Update button hover states based on mouse position.
        
        Args:
            pos (tuple): Mouse coordinates (x, y)
        """
        for button in self.buttons:
            button["hover"] = button["rect"].collidepoint(pos)