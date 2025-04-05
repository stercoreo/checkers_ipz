import pygame
from checker import Checker

class Board:
    """Manages all game board operations and rendering with unified visual style."""

    def __init__(self, width, height):
        """
        Initialize game board with synchronized color scheme.
        
        Args:
            width (int): Pixel width of board surface
            height (int): Pixel height of board surface
        """
        self.rows = 8
        self.cols = 8
        self.width = width
        self.height = height
        self.cell_size = width // 8
        self.board = []
        
        # Master color definitions for entire application
        self.colors = {
            # Board colors
            "light": (235, 227, 211),  # Cream (light squares)
            "dark": (94, 87, 87),      # Taupe (dark squares)
            
            # UI colors
            "background": (30, 30, 40),    # Dark blue background
            "panel": (40, 40, 50, 200),    # Semi-transparent UI panels
            "highlight": (180, 150, 100),  # Gold accents
            
            # Text colors
            "text": (220, 200, 180),       # Primary text
            "text_shadow": (20, 20, 20),   # Text shadow
            
            # Button colors
            "button_normal": (70, 70, 90),
            "button_hover": (100, 100, 120),
            "button_text": (220, 210, 190),
            "button_border": (150, 140, 130)
        }
        
        self.create_board()
        self.captured_checkers = []

    def create_board(self):
        """Initialize board with standard starting positions."""
        for row in range(self.rows):
            self.board.append([])
            for col in range(self.cols):
                if (row + col) % 2 == 1:  # Only dark squares contain pieces
                    if row < 3:
                        self.board[row].append(Checker('white', row, col, self.cell_size, self.colors))
                    elif row > 4:
                        self.board[row].append(Checker('black', row, col, self.cell_size, self.colors))
                    else:
                        self.board[row].append(None)
                else:
                    self.board[row].append(None)

    def draw(self, screen):
        """
        Render complete board state with unified visual style.
        
        Args:
            screen: Pygame surface to render onto
        """
        # Draw background
        screen.fill(self.colors["background"])
        
        # Draw checkerboard pattern
        for row in range(self.rows):
            for col in range(self.cols):
                color = self.colors["light"] if (row + col) % 2 == 0 else self.colors["dark"]
                pygame.draw.rect(screen, color, 
                               (col * self.cell_size,
                                row * self.cell_size,
                                self.cell_size,
                                self.cell_size))
        
        # Draw captured pieces (for animations)
        for checker in self.captured_checkers:
            checker.is_capturing = True
            checker.draw(screen)
        
        # Draw active pieces
        for row in range(self.rows):
            for col in range(self.cols):
                checker = self.board[row][col]
                if checker:
                    checker.is_capturing = False
                    checker.draw(screen)

    def get_checker(self, row, col):
        """
        Retrieve checker at specified position.
        
        Args:
            row (int): Row index (0-7)
            col (int): Column index (0-7)
            
        Returns:
            Checker: The checker object or None
        """
        if 0 <= row < self.rows and 0 <= col < self.cols:
            return self.board[row][col]
        return None

    def move(self, checker, row, col):
        """
        Move checker to new position.
        
        Args:
            checker (Checker): Checker to move
            row (int): Destination row
            col (int): Destination column
        """
        self.board[checker.row][checker.col] = None
        self.board[row][col] = checker
        checker.move_to(row, col)

    def remove(self, checkers):
        """
        Remove checkers from board (capture).
        
        Args:
            checkers (list): Checkers to remove
        """
        self.captured_checkers.extend(checkers)
        for checker in checkers:
            if checker:
                self.board[checker.row][checker.col] = None

    def winner(self):
        """
        Determine game winner based on remaining pieces.
        
        Returns:
            str: 'white', 'black', or None
        """
        white_count = sum(1 for row in self.board 
                         for checker in row 
                         if checker and checker.color == 'white')
        black_count = sum(1 for row in self.board 
                         for checker in row 
                         if checker and checker.color == 'black')
        
        if white_count == 0:
            return 'black'
        if black_count == 0:
            return 'white'
        return None

    def clear_captured(self):
        """Reset captured pieces list."""
        self.captured_checkers = []

    def get_valid_moves(self, checker):
        """
        Calculate all valid moves for specified checker.
        
        Args:
            checker (Checker): Checker to evaluate
            
        Returns:
            dict: Valid moves as {(row,col): [captured_checkers]}
        """
        moves = {}
        left = checker.col - 1
        right = checker.col + 1
        row = checker.row
        
        # Check capture moves first
        captures = {}
        if checker.color == 'black' or checker.is_king:
            captures.update(self._traverse_left(row-1, max(row-3, -1), -1, checker.color, left))
            captures.update(self._traverse_right(row-1, max(row-3, -1), -1, checker.color, right))
        
        if checker.color == 'white' or checker.is_king:
            captures.update(self._traverse_left(row+1, min(row+3, self.rows), 1, checker.color, left))
            captures.update(self._traverse_right(row+1, min(row+3, self.rows), 1, checker.color, right))
        
        # Mandatory capture rule
        if any(captures.values()):
            return {k:v for k,v in captures.items() if v}
        
        # Regular moves
        if checker.color == 'black' or checker.is_king:
            if row-1 >= 0 and left >= 0 and not self.board[row-1][left]:
                moves[(row-1, left)] = []
            if row-1 >= 0 and right < self.cols and not self.board[row-1][right]:
                moves[(row-1, right)] = []
        
        if checker.color == 'white' or checker.is_king:
            if row+1 < self.rows and left >= 0 and not self.board[row+1][left]:
                moves[(row+1, left)] = []
            if row+1 < self.rows and right < self.cols and not self.board[row+1][right]:
                moves[(row+1, right)] = []
        
        return moves

    def _traverse_left(self, start, stop, step, color, left, skipped=[]):
        """
        Recursively search for valid left diagonal moves.
        
        Args:
            start (int): Starting row
            stop (int): Stop row
            step (int): Direction (-1 up, 1 down)
            color (str): Checker color
            left (int): Current left position
            skipped (list): Captured checkers
            
        Returns:
            dict: Valid moves in this direction
        """
        moves = {}
        last = []
        for r in range(start, stop, step):
            if left < 0:
                break
            
            current = self.board[r][left]
            if not current:
                if skipped and not last:
                    break
                if skipped:
                    moves[(r, left)] = last + skipped
                else:
                    moves[(r, left)] = last
                
                if last:
                    if step == -1:
                        row = max(r-3, -1)
                    else:
                        row = min(r+3, self.rows)
                    moves.update(self._traverse_left(r+step, row, step, color, left-1, skipped=last))
                    moves.update(self._traverse_right(r+step, row, step, color, left+1, skipped=last))
                break
            elif current.color == color:
                break
            else:
                last = [current]
            
            left -= 1
        
        return moves

    def _traverse_right(self, start, stop, step, color, right, skipped=[]):
        """
        Recursively search for valid right diagonal moves.
        
        Args:
            start (int): Starting row
            stop (int): Stop row
            step (int): Direction (-1 up, 1 down)
            color (str): Checker color
            right (int): Current right position
            skipped (list): Captured checkers
            
        Returns:
            dict: Valid moves in this direction
        """
        moves = {}
        last = []
        for r in range(start, stop, step):
            if right >= self.cols:
                break
            
            current = self.board[r][right]
            if not current:
                if skipped and not last:
                    break
                if skipped:
                    moves[(r, right)] = last + skipped
                else:
                    moves[(r, right)] = last
                
                if last:
                    if step == -1:
                        row = max(r-3, -1)
                    else:
                        row = min(r+3, self.rows)
                    moves.update(self._traverse_left(r+step, row, step, color, right-1, skipped=last))
                    moves.update(self._traverse_right(r+step, row, step, color, right+1, skipped=last))
                break
            elif current.color == color:
                break
            else:
                last = [current]
            
            right += 1
        
        return moves