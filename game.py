import pygame
import sys
from board import Board
from ai import AIPlayer

class Game:
    """
    Main game controller class for Checkers.
    Handles game logic, turns, moves, and rendering.
    """
    def __init__(self, mode='local', difficulty=AIPlayer.DIFFICULTY_MEDIUM):
        """
        Initialize game state and components.
        
        Args:
            mode (str): 'local' for PvP or 'ai' for vs computer
            difficulty (int): AI difficulty level (0-2)
        """
        pygame.init()
        self.width = 800      # Window width
        self.height = 850     # Window height (extra 50px for UI)
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Checkers")
        
        # Game components
        self.clock = pygame.time.Clock()
        self.board = Board(800, 800)  # Game board
        self.ai_player = AIPlayer(difficulty) if mode == 'ai' else None
        
        # Game state
        self.mode = mode              # Game mode
        self.difficulty = difficulty  # AI difficulty
        self.turn = 'white'           # Current player
        self.selected = None          # Currently selected checker
        self.valid_moves = {}         # Valid moves for selected checker
        self.game_over = False        # Game completion flag
        self.animating = False        # Animation in progress flag
        
        # Multi-capture state
        self.multi_capture = []       # Stores multi-capture moves
        self.current_capture_index = 0 # Current step in multi-capture
        self.must_capture = False     # Flag for mandatory capture

    def get_all_valid_moves(self, color):
        """
        Get all valid moves for all checkers of specified color.
        Prioritizes captures if available (mandatory capture rule).
        
        Args:
            color (str): 'white' or 'black'
            
        Returns:
            dict: { (row,col): { (move_row,move_col): [captured_checkers] } }
        """
        all_moves = {}
        has_captures = False
        
        # First check all checkers for capture moves
        for row in range(self.board.rows):
            for col in range(self.board.cols):
                checker = self.board.get_checker(row, col)
                if checker and checker.color == color:
                    moves = self.get_valid_moves(checker)
                    if moves:
                        # Check if this checker has any capture moves
                        for move, captured in moves.items():
                            if captured:  # This is a capture move
                                has_captures = True
                                break
                        
                        if has_captures:
                            # Only include capture moves if available
                            capturing_moves = {k:v for k,v in moves.items() if v}
                            if capturing_moves:
                                all_moves[(row, col)] = capturing_moves
                        else:
                            # No captures - include all moves
                            all_moves[(row, col)] = moves
        
        # If captures exist, filter out non-capture moves
        if has_captures:
            return {k:v for k,v in all_moves.items() 
                   if any(captured for captured in v.values())}
        return all_moves

    def select(self, row, col):
        """
        Handle checker selection or move execution.
        
        Args:
            row (int): Board row
            col (int): Board column
            
        Returns:
            bool: True if selection/move was valid
        """
        if self.game_over or self.animating:
            return False
            
        checker = self.board.get_checker(row, col)
        
        # Check if there are any mandatory captures for current player
        all_moves = self.get_all_valid_moves(self.turn)
        must_capture = any(any(captured for captured in moves.values()) 
                         for moves in all_moves.values())
        
        # Select own checker if not in multi-capture
        if checker and checker.color == self.turn and not self.multi_capture:
            # If must capture, only allow selection of checkers that can capture
            if must_capture:
                # Check if this checker has any capture moves
                checker_moves = self.get_valid_moves(checker)
                checker_can_capture = any(captured for captured in checker_moves.values())
                if not checker_can_capture:
                    return False  # Can't select this checker when must capture
            
            self.selected = checker
            self.valid_moves = self.get_valid_moves(checker)
            
            # Enforce mandatory capture rule - filter to only capture moves if any exist
            if must_capture:
                self.valid_moves = {k:v for k,v in self.valid_moves.items() if v}
                if not self.valid_moves:  # No valid capture moves (shouldn't happen due to above check)
                    self.selected = None
                    return False
            return True
        
        # Execute move if valid
        elif self.selected and (row, col) in self.valid_moves:
            # Additional check to prevent moving non-capturing pieces when captures are available
            if must_capture and not self.valid_moves[(row, col)]:
                return False  # Trying to make non-capture move when capture is mandatory
                
            self.handle_move(row, col)
            return True
        
        # Invalid selection
        self.selected = None
        self.valid_moves = {}
        return False

    def handle_move(self, row, col):
        """
        Process a move to the specified position.
        Handles both single captures and multi-captures.
        """
        self.animating = True
        checker = self.selected
        captured = self.valid_moves[(row, col)]
        
        # Handle multi-capture (king moves)
        if len(captured) > 1:
            self.multi_capture = self._split_multi_capture(checker, row, col, captured)
            self.current_capture_index = 0
            self.process_next_capture()
        else:
            self._execute_single_move(checker, row, col, captured)

    def _split_multi_capture(self, checker, target_row, target_col, captured):
        """
        Split a multi-capture move into individual steps.
        
        Returns:
            list: Sequence of move dicts with intermediate positions
        """
        moves = []
        current_row, current_col = checker.row, checker.col
        
        for cap in captured:
            # Calculate intermediate jump position
            mid_row = (current_row + cap.row) // 2
            mid_col = (current_col + cap.col) // 2
            
            moves.append({
                'checker': checker,
                'from_pos': (current_row, current_col),
                'to_pos': (mid_row, mid_col),
                'captured': [cap]
            })
            current_row, current_col = mid_row, mid_col
        
        # Add final move to target position
        moves.append({
            'checker': checker,
            'from_pos': (current_row, current_col),
            'to_pos': (target_row, target_col),
            'captured': []
        })
        
        return moves

    def process_next_capture(self):
        """Execute the next step in a multi-capture sequence."""
        if self.current_capture_index >= len(self.multi_capture):
            return
            
        move = self.multi_capture[self.current_capture_index]
        checker = move['checker']
        from_row, from_col = move['from_pos']
        to_row, to_col = move['to_pos']
        captured = move['captured']
        
        if captured:
            self.board.remove(captured)
        
        self.board.move(checker, to_row, to_col)
        self.animate_move(checker, self.on_capture_animation_done)

    def on_capture_animation_done(self):
        """Callback when capture animation completes."""
        self.current_capture_index += 1
        
        if self.current_capture_index < len(self.multi_capture):
            self.process_next_capture()
        else:
            self._finish_multicapture()

    def _finish_multicapture(self):
        """Finalize multi-capture sequence and check for additional captures."""
        checker = self.multi_capture[-1]['checker']
        self.multi_capture = []
        self.current_capture_index = 0
        
        # Check for promotion to king
        row, col = checker.row, checker.col
        if ((row == 0 and checker.color == 'black') or 
            (row == self.board.rows-1 and checker.color == 'white')):
            checker.is_king = True
        
        # Check for additional captures
        self.valid_moves = self.get_valid_moves(checker)
        has_additional_captures = any(captured for captured in self.valid_moves.values())
        
        if has_additional_captures and (checker.is_king or not any(c.is_king for c in [checker])):
            self.selected = checker  # Continue capturing
        else:
            self.change_turn()

    def _execute_single_move(self, checker, row, col, captured):
        """Execute a single move (non-capture or single capture)."""
        if captured:
            self.board.remove(captured)
        
        self.board.move(checker, row, col)
        self.animate_move(checker, lambda: self._on_single_move_complete(checker, row, col))

    def _on_single_move_complete(self, checker, row, col):
        """Handle completion of a single move."""
        # Check for promotion
        if ((row == 0 and checker.color == 'black') or 
            (row == self.board.rows-1 and checker.color == 'white')):
            checker.is_king = True
        
        self.change_turn()

    def animate_move(self, checker, callback):
        """
        Animate checker movement.
        
        Args:
            checker: Checker to animate
            callback: Function to call when animation completes
        """
        def animation_loop():
            still_animating = checker.update()
            self.draw()
            pygame.display.flip()
            
            if still_animating:
                self.clock.tick(60)
                pygame.time.delay(10)
                animation_loop()
            else:
                self.board.clear_captured()
                self.animating = False
                callback()
        
        animation_loop()

    def change_turn(self):
        """Switch turns and check game state."""
        self.selected = None
        self.valid_moves = {}
        self.turn = 'black' if self.turn == 'white' else 'white'
        
        # Check for winner
        winner = self._check_game_over() or self.board.winner()
        if winner:
            self.game_over = True
            return
        
        # AI move if applicable
        if self.mode == 'ai' and self.turn == 'black' and not self.game_over:
            self.ai_move()

    def _check_game_over(self):
        """
        Check if current player has no valid moves.
        
        Returns:
            str: Winning color if game over, else None
        """
        current_moves = self.get_all_valid_moves(self.turn)
        if not current_moves:
            return 'black' if self.turn == 'white' else 'white'
        return None

    def ai_move(self):
        """Execute AI move if valid moves exist."""
        if not self.ai_player or self.game_over:
            return
            
        ai_valid_moves = self.get_all_valid_moves('black')
        if not ai_valid_moves:
            self.change_turn()
            return
            
        move = self.ai_player.get_move(self.board, ai_valid_moves)
        if move:
            start_pos, end_pos, _ = move
            self.select(*start_pos)
            if self.selected:  # Ensure valid selection
                self.handle_move(*end_pos)
        else:
            self.change_turn()

    def get_valid_moves(self, checker):
        """
        Get all valid moves for a specific checker.
        Implements mandatory capture rule.
        
        Returns:
            dict: { (row,col): [captured_checkers] }
        """
        moves = {}
        left = checker.col - 1
        right = checker.col + 1
        row = checker.row
        
        # Check capture moves first (mandatory)
        captures = {}
        if checker.color == 'black' or checker.is_king:
            captures.update(self._traverse_left(row-1, max(row-3, -1), -1, checker.color, left))
            captures.update(self._traverse_right(row-1, max(row-3, -1), -1, checker.color, right))
        
        if checker.color == 'white' or checker.is_king:
            captures.update(self._traverse_left(row+1, min(row+3, self.board.rows), 1, checker.color, left))
            captures.update(self._traverse_right(row+1, min(row+3, self.board.rows), 1, checker.color, right))
        
        # If captures exist, return only them
        if any(captures.values()):
            return {k:v for k,v in captures.items() if v}
        
        # No captures - return regular moves
        if checker.color == 'black' or checker.is_king:
            if row-1 >= 0 and left >= 0 and not self.board.get_checker(row-1, left):
                moves[(row-1, left)] = []
            if row-1 >= 0 and right < self.board.cols and not self.board.get_checker(row-1, right):
                moves[(row-1, right)] = []
        
        if checker.color == 'white' or checker.is_king:
            if row+1 < self.board.rows and left >= 0 and not self.board.get_checker(row+1, left):
                moves[(row+1, left)] = []
            if row+1 < self.board.rows and right < self.board.cols and not self.board.get_checker(row+1, right):
                moves[(row+1, right)] = []
        
        return moves

    def _traverse_left(self, start, stop, step, color, left, skipped=[]):
        """
        Recursive helper to find valid diagonal moves to the left.
        Handles multiple jumps for captures.
        """
        moves = {}
        last = []
        for r in range(start, stop, step):
            if left < 0:
                break
            
            current = self.board.get_checker(r, left)
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
                        row = min(r+3, self.board.rows)
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
        """Recursive helper to find valid diagonal moves to the right."""
        moves = {}
        last = []
        for r in range(start, stop, step):
            if right >= self.board.cols:
                break
            
            current = self.board.get_checker(r, right)
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
                        row = min(r+3, self.board.rows)
                    moves.update(self._traverse_left(r+step, row, step, color, right-1, skipped=last))
                    moves.update(self._traverse_right(r+step, row, step, color, right+1, skipped=last))
                break
            elif current.color == color:
                break
            else:
                last = [current]
            
            right += 1
        
        return moves

    def draw(self):
        """Render the game state."""
        self.board.draw(self.screen)
        
        # Draw turn indicator with larger area and moved up
        indicator_height = 60  # Increased height
        indicator_y = 790     # Moved up by 10 pixels
        pygame.draw.rect(self.screen, (240, 240, 240), (0, indicator_y, 800, indicator_height))
        pygame.draw.line(self.screen, (200, 200, 200), (0, indicator_y), (800, indicator_y), 2)
        
        # Create text background for better visibility
        text_bg = pygame.Surface((800, indicator_height), pygame.SRCALPHA)
        text_bg.fill((240, 240, 240, 200))
        self.screen.blit(text_bg, (0, indicator_y))
        
        font = pygame.font.SysFont('Arial', 32)
        turn_text = f"{self.turn.capitalize()}'s turn"
        
        # Check for mandatory captures
        must_capture = any(
            any(captured for captured in moves.values())
            for moves in self.get_all_valid_moves(self.turn).values()
        )
        
        if must_capture:
            turn_text += " (Must capture!)"
            # Highlight checkers that must capture
            for row in range(self.board.rows):
                for col in range(self.board.cols):
                    checker = self.board.get_checker(row, col)
                    if checker and checker.color == self.turn:
                        moves = self.get_valid_moves(checker)
                        if any(moves.values()):  # Has capture moves
                            pygame.draw.circle(
                                self.screen, (255, 0, 0, 150),
                                (col*self.board.cell_size + self.board.cell_size//2,
                                 row*self.board.cell_size + self.board.cell_size//2),
                                self.board.cell_size//2 - 5, 3
                            )
        
        if self.mode == 'ai' and self.turn == 'black':
            turn_text += [" (Easy)", " (Medium)", " (Hard)"][self.difficulty]
        
        text = font.render(turn_text, True, (0, 0, 0))
        # Center text vertically in the indicator area
        text_y = indicator_y + (indicator_height - text.get_height()) // 2
        self.screen.blit(text, (self.width//2 - text.get_width()//2, text_y))
        
        # Highlight valid moves
        if self.selected:
            for move, captured in self.valid_moves.items():
                row, col = move
                s = pygame.Surface((self.board.cell_size, self.board.cell_size), pygame.SRCALPHA)
                color = (255, 0, 0, 150) if captured else (0, 255, 0, 100)
                pygame.draw.circle(s, color, 
                                 (self.board.cell_size//2, self.board.cell_size//2),
                                 self.board.cell_size//4)
                self.screen.blit(s, (col*self.board.cell_size, row*self.board.cell_size))
        
        # Draw game over screen if needed
        if self.game_over:
            self._draw_game_over()

    def _draw_game_over(self):
        """Render game over screen with winner and menu button."""
        winner = self.board.winner()
        font = pygame.font.SysFont('Arial', 72)
        text = font.render(f"{winner.capitalize()} wins!", True, (255, 215, 0))
        text_rect = text.get_rect(center=(self.width//2, self.height//2))
        
        # Semi-transparent background
        s = pygame.Surface((text_rect.width + 40, text_rect.height + 40), pygame.SRCALPHA)
        s.fill((0, 0, 0, 200))
        self.screen.blit(s, (text_rect.x-20, text_rect.y-20))
        self.screen.blit(text, text_rect)
        
        # Return to menu button
        back_rect = pygame.Rect(self.width//2-150, self.height//2+100, 300, 50)
        pygame.draw.rect(self.screen, (70, 130, 180), back_rect)
        pygame.draw.rect(self.screen, (0, 0, 0), back_rect, 2)
        
        text = pygame.font.SysFont('Arial', 36).render(
            "Return to Menu", True, (255, 255, 255))
        self.screen.blit(text, (
            back_rect.centerx - text.get_width()//2,
            back_rect.centery - text.get_height()//2
        ))
        
        return back_rect

    def run(self):
        """Main game loop."""
        running = True
        while running:
            back_button = None
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    
                    if self.game_over:
                        back_button = self._draw_game_over()
                        if back_button and back_button.collidepoint(pos):
                            return "menu"
                    elif not self.animating and self.turn == 'white':
                        row = pos[1] // self.board.cell_size
                        col = pos[0] // self.board.cell_size
                        self.select(row, col)
            
            # AI move
            if (not self.game_over and not self.animating and 
                self.turn == 'black' and self.mode == 'ai'):
                self.ai_move()
            
            self.draw()
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()