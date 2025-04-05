import pygame

class GameMenu:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.buttons = [
            {"text": "1 vs 1 (Local)", "action": "local", "rect": None},
            {"text": "vs AI", "action": "ai", "rect": None},
            {"text": "Quit", "action": "quit", "rect": None}
        ]
        self.font = pygame.font.SysFont('Arial', 36)
        self._init_buttons()

    def _init_buttons(self):
        button_width = 300
        button_height = 60
        start_y = self.height // 2 - 100
        
        for i, button in enumerate(self.buttons):
            x = self.width // 2 - button_width // 2
            y = start_y + i * (button_height + 20)
            button["rect"] = pygame.Rect(x, y, button_width, button_height)

    def draw(self, screen):
        screen.fill((50, 50, 50))
        
        title_font = pygame.font.SysFont('Arial', 48)
        title = title_font.render("CHECKERS", True, (255, 255, 255))
        screen.blit(title, (self.width // 2 - title.get_width() // 2, 100))

        for button in self.buttons:
            pygame.draw.rect(screen, (70, 130, 180), button["rect"])
            pygame.draw.rect(screen, (0, 0, 0), button["rect"], 2)
            
            text = self.font.render(button["text"], True, (255, 255, 255))
            text_rect = text.get_rect(center=button["rect"].center)
            screen.blit(text, text_rect)

    def handle_click(self, pos):
        for button in self.buttons:
            if button["rect"].collidepoint(pos):
                return button["action"]
        return None