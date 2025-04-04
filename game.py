import pygame
from board import Board

class Game:
    def __init__(self, width=800, height=800):
        pygame.init()
        self.width = width
        self.height = height
        self.cell_size = width // 8
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Шашки")
        self.board = Board(8, 8, self.cell_size)
        self.turn = 'white'
        self.valid_moves = {}
    
    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    row, col = pos[1] // self.cell_size, pos[0] // self.cell_size
                    self.select(row, col)
            
            self.draw()
            pygame.display.update()
        
        pygame.quit()
    
    def select(self, row, col):
        checker = self.board.get_checker(row, col)
        
        if checker and checker.color == self.turn:
            self.board.selected = checker
            self.valid_moves = self.get_valid_moves(checker)
            return True
        
        if self.board.selected:
            if (row, col) in self.valid_moves:
                self.board.move(self.board.selected, row, col)
                self.change_turn()
        
        return False
    
    def get_valid_moves(self, checker):
        moves = {}
        left = checker.col - 1
        right = checker.col + 1
        row = checker.row
        
        if checker.color == 'white' or checker.is_king:
            moves.update(self._traverse_left(row-1, max(row-3, -1), -1, checker.color, left))
            moves.update(self._traverse_right(row-1, max(row-3, -1), -1, checker.color, right))
        
        if checker.color == 'black' or checker.is_king:
            moves.update(self._traverse_left(row+1, min(row+3, 8), 1, checker.color, left))
            moves.update(self._traverse_right(row+1, min(row+3, 8), 1, checker.color, right))
        
        return moves
    
    def _traverse_left(self, start, stop, step, color, left, skipped=[]):
        moves = {}
        last = []
        for r in range(start, stop, step):
            if left < 0:
                break
            
            current = self.board.get_checker(r, left)
            if current is None:
                if skipped and not last:
                    break
                moves[(r, left)] = last
                break
            elif current.color == color:
                break
            else:
                last = [current]
            
            left -= 1
        
        return moves
    
    def _traverse_right(self, start, stop, step, color, right, skipped=[]):
        moves = {}
        last = []
        for r in range(start, stop, step):
            if right >= 8:
                break
            
            current = self.board.get_checker(r, right)
            if current is None:
                if skipped and not last:
                    break
                moves[(r, right)] = last
                break
            elif current.color == color:
                break
            else:
                last = [current]
            
            right += 1
        
        return moves
    
    def change_turn(self):
        self.valid_moves = {}
        self.board.selected = None
        self.turn = 'black' if self.turn == 'white' else 'white'
    
    def draw(self):
        self.board.draw(self.screen)
        self.draw_valid_moves()
    
    def draw_valid_moves(self):
        for move in self.valid_moves:
            row, col = move
            pygame.draw.circle(self.screen, (0, 255, 0), 
                             (col * self.cell_size + self.cell_size // 2, 
                              row * self.cell_size + self.cell_size // 2), 15)