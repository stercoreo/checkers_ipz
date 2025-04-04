import pygame

class Checker:
    def __init__(self, color, row, col, cell_size):
        self.color = color  # 'white' или 'black'
        self.row = row
        self.col = col
        self.cell_size = cell_size
        self.is_king = False
        self.x = 0
        self.y = 0
        self.calc_pos()
    
    def calc_pos(self):
        self.x = self.col * self.cell_size + self.cell_size // 2
        self.y = self.row * self.cell_size + self.cell_size // 2
    
    def make_king(self):
        self.is_king = True
    
    def draw(self, screen):
        radius = self.cell_size // 2 - 10
        pygame.draw.circle(screen, self.get_color(), (self.x, self.y), radius)
        if self.is_king:
            pygame.draw.circle(screen, (255, 215, 0), (self.x, self.y), radius // 2)
    
    def get_color(self):
        return (255, 255, 255) if self.color == 'white' else (50, 50, 50)
    
    def move(self, row, col):
        self.row = row
        self.col = col
        self.calc_pos()