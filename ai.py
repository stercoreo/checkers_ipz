# ai.py
import random

class AIPlayer:
    """
    AI player for checkers with three difficulty levels.
    Handles move selection based on difficulty.
    """
    # Difficulty constants
    DIFFICULTY_EASY = 0    # Makes random moves
    DIFFICULTY_MEDIUM = 1  # Prioritizes captures
    DIFFICULTY_HARD = 2    # Prioritizes captures and promotions
    
    def __init__(self, difficulty=DIFFICULTY_MEDIUM):
        """
        Initialize AI player with specified difficulty.
        
        Args:
            difficulty (int): Difficulty level (0-2)
        """
        self.difficulty = difficulty

    def get_move(self, board, valid_moves):
        """
        Select a move based on AI difficulty.
        
        Args:
            board (Board): Current game board
            valid_moves (dict): All valid moves available
            
        Returns:
            tuple: ((start_row, start_col), (end_row, end_col), [captured_checkers])
                   or None if no moves available
        """
        # Flatten moves dictionary into list of all possible moves
        all_moves = []
        for (start_row, start_col), moves in valid_moves.items():
            for (end_row, end_col), captured in moves.items():
                all_moves.append(((start_row, start_col), (end_row, end_col), captured))
        
        if not all_moves:
            return None

        # Select move based on difficulty
        if self.difficulty == self.DIFFICULTY_EASY:
            return self.get_easy_move(all_moves)
        elif self.difficulty == self.DIFFICULTY_MEDIUM:
            return self.get_medium_move(all_moves, board)
        else:
            return self.get_hard_move(all_moves, board)

    def get_easy_move(self, moves):
        """Random move selection (easiest difficulty)."""
        return random.choice(moves)

    def get_medium_move(self, moves, board):
        """
        Prioritize captures, then random move (medium difficulty).
        
        Args:
            moves (list): All possible moves
            board (Board): Game board (unused in this difficulty)
        """
        # Filter for capturing moves
        capturing_moves = [m for m in moves if len(m[2]) > 0]
        if capturing_moves:
            # Find moves with maximum captures
            max_captures = max(len(m[2]) for m in capturing_moves)
            best_moves = [m for m in capturing_moves if len(m[2]) == max_captures]
            return random.choice(best_moves)
        return random.choice(moves)

    def get_hard_move(self, moves, board):
        """
        Prioritize captures and promotions (hardest difficulty).
        
        Args:
            moves (list): All possible moves
            board (Board): Game board (used to check checker state)
        """
        # First look for capturing moves
        capturing_moves = [m for m in moves if len(m[2]) > 0]
        if capturing_moves:
            max_captures = max(len(m[2]) for m in capturing_moves)
            best_moves = [m for m in capturing_moves if len(m[2]) == max_captures]
            
            # Within best capturing moves, look for promotion opportunities
            promoting_moves = []
            for move in best_moves:
                start_pos, end_pos, _ = move
                checker = board.get_checker(*start_pos)
                if not checker.is_king:
                    # Check if move would promote to king
                    if (checker.color == 'black' and end_pos[0] == 0) or \
                       (checker.color == 'white' and end_pos[0] == board.rows - 1):
                        promoting_moves.append(move)
            
            if promoting_moves:
                return random.choice(promoting_moves)
            return random.choice(best_moves)
        
        # If no captures, look for promotion moves
        promotion_moves = []
        for move in moves:
            start_pos, end_pos, _ = move
            checker = board.get_checker(*start_pos)
            if not checker.is_king:
                # Black moves up (lower row numbers), white moves down
                if checker.color == 'black' and end_pos[0] < start_pos[0]:
                    promotion_moves.append(move)
                elif checker.color == 'white' and end_pos[0] > start_pos[0]:
                    promotion_moves.append(move)
        
        if promotion_moves:
            return random.choice(promotion_moves)
        
        # Default to random move
        return random.choice(moves)