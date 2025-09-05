import chess
import threading

class GameState:
    """Manages the game state and transitions between different states."""
    
    def __init__(self):
        """Initialize the game state."""
        self.board = chess.Board()
        self.player_color = chess.WHITE
        self.difficulty = None
        self.game_state = "menu"  # menu, color_select, difficulty, playing, game_over, analysis
        self.result = None
        self.promotion_choice = None
        
        # Move history for navigating backward/forward
        self.move_history = [self.board.copy()]
        self.current_move_index = 0
        self.last_move = None
        
        # Game statistics
        self.game_count = {"player": 0, "stockfish": 0, "draw": 0}
        
        # Board interaction
        self.selected_square = None
        self.legal_moves_squares = []
        
        # Evaluation
        self.evaluation_mode = False
        self.show_best_move = False
        
        # Promotion handling
        self.pending_promotion = None
        
        # Draw request handling
        self.draw_requested = False
        
        # Callbacks for when state or position changes
        self.state_change_callback = None
        self.position_change_callback = None
    
    def set_state_change_callback(self, callback):
        """Set a callback function to be called when the game state changes."""
        self.state_change_callback = callback
    
    def set_position_change_callback(self, callback):
        """Set a callback function to be called when the board position changes."""
        self.position_change_callback = callback
    
    def set_game_state(self, state):
        """Change the current game state."""
        old_state = self.game_state
        self.game_state = state
        
        if state == "menu":
            self.reset_game()
            self.game_count = {"player": 0, "stockfish": 0, "draw": 0}
        
        if self.state_change_callback:
            self.state_change_callback(old_state, state)
    
    def reset_game(self):
        """Reset the game to its initial state."""
        self.board.reset()
        self.move_history = [self.board.copy()]
        self.current_move_index = 0
        self.last_move = None
        self.selected_square = None
        self.evaluation_mode = False
        self.show_best_move = False
        self.legal_moves_squares = []
        self.draw_requested = False
    
    def make_move(self, move):
        """Make a move on the board."""
        self.board.push(move)
        self.last_move = move
        
        # Update move history
        self.move_history = self.move_history[:self.current_move_index + 1]
        self.move_history.append(self.board.copy())
        self.current_move_index = len(self.move_history) - 1
        
        self.check_game_end()
        self.legal_moves_squares = []
    
    def go_back(self):
        """Navigate backward in move history."""
        if self.current_move_index > 0:
            self.current_move_index -= 1
            self.board = self.move_history[self.current_move_index].copy()
            self.last_move = self.board.move_stack[-1] if self.board.move_stack else None
            
            # Notify position change for evaluation updates
            if self.position_change_callback:
                self.position_change_callback(self.board)
    
    def go_forward(self):
        """Navigate forward in move history."""
        if self.current_move_index < len(self.move_history) - 1:
            self.current_move_index += 1
            self.board = self.move_history[self.current_move_index].copy()
            self.last_move = self.board.move_stack[-1] if self.board.move_stack else None
            
            # Notify position change for evaluation updates
            if self.position_change_callback:
                self.position_change_callback(self.board)
    
    def start_game(self, mode, difficulty=None):
        """Start a new game with the specified mode and difficulty."""
        self.game_state = "playing"
        self.reset_game()
        # Keep the player color that was already set
        
        if mode == "singleplayer":
            self.difficulty = difficulty
        else:
            self.difficulty = None
    
    def check_game_end(self):
        """Check if the game has ended and set the appropriate result."""
        if self.board.is_game_over():
            if self.board.is_checkmate():
                winner = "Black" if self.board.turn == chess.WHITE else "White"
                self.end_game(f"{winner} wins by checkmate")
            elif self.board.is_stalemate():
                self.end_game("Game drawn by stalemate")
            elif self.board.is_insufficient_material():
                self.end_game("Game drawn due to insufficient material")
            elif self.board.is_fifty_moves():
                self.end_game("Game drawn by fifty-move rule")
            elif self.board.is_repetition():
                self.end_game("Game drawn by repetition")
    
    def end_game(self, result):
        """End the game with the specified result."""
        self.game_state = "game_over"
        self.result = result
        
        # Update game statistics
        if "White wins" in result:
            self.game_count["player" if self.player_color == chess.WHITE else "stockfish"] += 1
        elif "Black wins" in result:
            self.game_count["player" if self.player_color == chess.BLACK else "stockfish"] += 1
        else:
            self.game_count["draw"] += 1
    
    def resign(self):
        """Resign the current game."""
        winner = "Black" if self.board.turn == chess.WHITE else "White"
        self.end_game(f"{winner} wins by resignation")
    
    def offer_draw(self):
        """Offer a draw in the current game."""
        self.end_game("Game drawn by agreement")
    
    def toggle_evaluation(self):
        """Toggle evaluation mode on/off."""
        self.evaluation_mode = not self.evaluation_mode
    
    def toggle_best_move(self):
        """Toggle showing best move on/off."""
        self.show_best_move = not self.show_best_move
    
    def reset_and_play(self):
        """Reset the game and start playing again."""
        old_state = self.game_state
        self.reset_game()
        self.game_state = "playing"
        
        # Trigger state change callback to reset engine state
        if self.state_change_callback:
            self.state_change_callback(old_state, "playing")
    
    def get_legal_moves_from_square(self, square):
        """Get all legal moves from a specific square."""
        return [move.to_square for move in self.board.legal_moves if move.from_square == square] 