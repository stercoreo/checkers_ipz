import pygame
from checker import Checker

class Board:
    def __init__(self, rows, cols, cell_size):
        self.rows = rows
        self.cols = cols
        self.cell_size = cell_size
        self.board = []
        self.selected = None
        self.create_board()
    
    def create_board(self):
        for row in range(self.rows):
            self.board.append([])
            for col in range(self.cols):
                if (row + col) % 2 == 1:
                    if row < 3:
                        self.board[row].append(Checker('white', row, col, self.cell_size))
                    elif row > 4:
                        self.board[row].append(Checker('black', row, col, self.cell_size))
                    else:
                        self.board[row].append(None)
                else:
                    self.board[row].append(None)
    
    def draw(self, screen):
        for row in range(self.rows):
            for col in range(self.cols):
                color = (235, 235, 208) if (row + col) % 2 == 0 else (119, 149, 86)
                pygame.draw.rect(screen, color, (col*self.cell_size, row*self.cell_size, self.cell_size, self.cell_size))
                
                checker = self.board[row][col]
                if checker:
                    checker.draw(screen)
    
    def get_checker(self, row, col):
        return self.board[row][col]
    
    def move(self, checker, row, col):
        self.board[checker.row][checker.col], self.board[row][col] = None, checker
        checker.move(row, col)
        
        if row == 0 and checker.color == 'black':
            checker.make_king()
        if row == self.rows - 1 and checker.color == 'white':
            checker.make_king()