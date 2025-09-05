import pygame
import chess
from utils import coords_to_square

class InputHandler:
    """Handles user input and event processing."""
    
    def __init__(self, game_state, engine_manager, ui_manager):
        """Initialize the input handler."""
        self.game_state = game_state
        self.engine_manager = engine_manager
        self.ui_manager = ui_manager
        
    def handle_event(self, event):
        """Handle a pygame event."""
        if event.type == pygame.QUIT:
            return False  # Signal to quit the game
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self.handle_mouse_click(event.pos)
        return True  # Continue the game
    
    def handle_mouse_click(self, pos):
        """Handle a mouse click at the given position."""
        if self.game_state.game_state == "menu":
            self.handle_menu_click(pos)
        elif self.game_state.game_state == "color_select":
            self.handle_color_click(pos)
        elif self.game_state.game_state == "difficulty":
            self.handle_difficulty_click(pos)
        elif self.game_state.game_state == "playing":
            self.handle_game_click(pos)
        elif self.game_state.game_state == "game_over":
            self.handle_game_over_click(pos)
        elif self.game_state.game_state == "analysis":
            self.handle_analysis_click(pos)
    
    def handle_menu_click(self, pos):
        """Handle a click on the main menu."""
        buttons = self.ui_manager.buttons
        
        if buttons["single player"].is_clicked(pos):
            self.game_state.set_game_state("color_select")
        elif buttons["two player"].is_clicked(pos):
            self.game_state.start_game("multiplayer")
        elif buttons["quit"].is_clicked(pos):
            return False  # Signal to quit the game
    
    def handle_color_click(self, pos):
        """Handle a click on the color selection menu."""
        buttons = self.ui_manager.buttons
        
        if buttons["play as white"].is_clicked(pos):
            self.game_state.player_color = chess.WHITE
            self.game_state.set_game_state("difficulty")
        elif buttons["play as black"].is_clicked(pos):
            self.game_state.player_color = chess.BLACK
            self.game_state.set_game_state("difficulty")
        elif buttons["back to menu"].is_clicked(pos):
            self.game_state.set_game_state("menu")
    
    def handle_difficulty_click(self, pos):
        """Handle a click on the difficulty selection menu."""
        buttons = self.ui_manager.buttons
        
        if buttons["easy"].is_clicked(pos):
            self.game_state.start_game("singleplayer", "easy")
            self.engine_manager.set_difficulty("easy")
            # If player is black, AI should move first
            if self.game_state.player_color == chess.BLACK:
                self.make_ai_move()
        elif buttons["medium"].is_clicked(pos):
            self.game_state.start_game("singleplayer", "medium")
            self.engine_manager.set_difficulty("medium")
            # If player is black, AI should move first
            if self.game_state.player_color == chess.BLACK:
                self.make_ai_move()
        elif buttons["hard"].is_clicked(pos):
            self.game_state.start_game("singleplayer", "hard")
            self.engine_manager.set_difficulty("hard")
            # If player is black, AI should move first
            if self.game_state.player_color == chess.BLACK:
                self.make_ai_move()
        elif buttons["back to menu"].is_clicked(pos):
            self.game_state.set_game_state("color_select")
    
    def handle_game_click(self, pos):
        """Handle a click during gameplay."""
        from config import BOARD_SIZE
        
        if pos[0] < BOARD_SIZE and pos[1] < BOARD_SIZE:
            self.handle_board_click(pos)
        else:
            self.handle_ui_click(pos)
    
    def handle_board_click(self, pos):
        """Handle a click on the chess board."""
        # Allow board interaction in playing mode, or in analysis mode, or when evaluation is active
        if not (self.game_state.game_state == "playing" or 
                self.game_state.game_state == "analysis" or
                (self.game_state.current_move_index == len(self.game_state.move_history) - 1) or
                self.game_state.evaluation_mode):
            return
        
        square = coords_to_square(pos[0], pos[1])
        
        # In analysis mode or when navigating with evaluation, allow move editing
        if (self.game_state.game_state == "analysis" or 
            (self.game_state.evaluation_mode and self.game_state.current_move_index < len(self.game_state.move_history) - 1)):
            # In pure analysis mode, allow all moves; in game evaluation mode, restrict to player color
            if (self.game_state.game_state == "playing" and 
                self.game_state.board.turn != self.game_state.player_color):
                return  # Don't allow editing bot's moves during gameplay
            
            # We're in the middle of the game, allow editing
            if self.game_state.selected_square is None:
                piece = self.game_state.board.piece_at(square)
                if piece and piece.color == self.game_state.board.turn:
                    self.game_state.selected_square = square
                    self.game_state.legal_moves_squares = self.game_state.get_legal_moves_from_square(square)
            else:
                move = chess.Move(self.game_state.selected_square, square)
                
                # Check for pawn promotion first (before checking if move is legal)
                piece = self.game_state.board.piece_at(self.game_state.selected_square)
                if (piece and piece.piece_type == chess.PAWN and
                    ((self.game_state.board.turn == chess.WHITE and chess.square_rank(square) == 7) or
                     (self.game_state.board.turn == chess.BLACK and chess.square_rank(square) == 0))):
                    
                    # Check if any promotion move to this square is legal
                    promotion_moves = [chess.Move(self.game_state.selected_square, square, promotion=p) 
                                     for p in [chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT]]
                    
                    if any(pm in self.game_state.board.legal_moves for pm in promotion_moves):
                        self.handle_promotion_dialog(move)
                        return  # Wait for promotion choice before making move
                
                # Normal move (non-promotion)
                if move in self.game_state.board.legal_moves:
                    self.game_state.make_move(move)
                    # Truncate move history and continue from this point
                    self.game_state.move_history = self.game_state.move_history[:self.game_state.current_move_index + 1]
                    
                    # Only make AI move if we're in playing mode and it's AI's turn
                    if (self.game_state.difficulty and 
                        self.game_state.game_state == "playing" and
                        self.game_state.board.turn != self.game_state.player_color):
                        self.make_ai_move()
                
                self.game_state.selected_square = None
                self.game_state.legal_moves_squares = []
        else:
            # Normal gameplay
            if self.game_state.selected_square is None:
                piece = self.game_state.board.piece_at(square)
                if piece and piece.color == self.game_state.board.turn:
                    self.game_state.selected_square = square
                    self.game_state.legal_moves_squares = self.game_state.get_legal_moves_from_square(square)
            else:
                move = chess.Move(self.game_state.selected_square, square)
                
                # Check for pawn promotion first (before checking if move is legal)
                piece = self.game_state.board.piece_at(self.game_state.selected_square)
                if (piece and piece.piece_type == chess.PAWN and
                    ((self.game_state.board.turn == chess.WHITE and chess.square_rank(square) == 7) or
                     (self.game_state.board.turn == chess.BLACK and chess.square_rank(square) == 0))):
                    
                    # Check if any promotion move to this square is legal
                    promotion_moves = [chess.Move(self.game_state.selected_square, square, promotion=p) 
                                     for p in [chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT]]
                    
                    if any(pm in self.game_state.board.legal_moves for pm in promotion_moves):
                        self.handle_promotion_dialog(move)
                        return  # Wait for promotion choice before making move
                
                # Normal move (non-promotion)
                if move in self.game_state.board.legal_moves:
                    self.game_state.make_move(move)
                    
                    if self.game_state.difficulty and self.game_state.board.turn != self.game_state.player_color:
                        self.make_ai_move()
                
                self.game_state.selected_square = None
                self.game_state.legal_moves_squares = []
    
    def handle_promotion_dialog(self, move):
        """Handle pawn promotion dialog."""
        # Store the promotion state in game state for main loop to handle
        self.game_state.pending_promotion = {
            'move': move,
            'dialog_active': True
        }
        
        # The main loop will handle the dialog display and input
    
    def handle_ui_click(self, pos):
        """Handle a click on the UI elements."""
        buttons = self.ui_manager.buttons
        
        if buttons["resign"].is_clicked(pos):
            self.game_state.resign()
        elif buttons["draw"].is_clicked(pos) and self.game_state.difficulty is None:
            # Handle draw request/accept for two-player games
            if not self.game_state.draw_requested:
                # First player requests draw
                self.game_state.draw_requested = True
            else:
                # Second player accepts draw
                self.game_state.offer_draw()
        elif buttons["decline draw"].is_clicked(pos) and self.game_state.difficulty is None:
            # Decline the draw request
            self.game_state.draw_requested = False
        elif buttons["menu"].is_clicked(pos):
            self.game_state.set_game_state("menu")
        elif buttons["back"].is_clicked(pos):
            self.game_state.go_back()
        elif buttons["forward"].is_clicked(pos):
            self.game_state.go_forward()
        elif buttons["evaluate"].is_clicked(pos):
            self.game_state.toggle_evaluation()
            self.handle_evaluation_toggle()
        elif buttons["best move"].is_clicked(pos) and self.game_state.evaluation_mode:
            self.game_state.toggle_best_move()
    
    def handle_game_over_click(self, pos):
        """Handle a click on the game over screen."""
        buttons = self.ui_manager.buttons
        
        if buttons["analyze"].is_clicked(pos):
            self.game_state.set_game_state("analysis")
            self.game_state.evaluation_mode = True
            self.handle_evaluation_toggle()
        elif buttons["play again"].is_clicked(pos):
            self.game_state.reset_and_play()
        elif buttons["main menu"].is_clicked(pos):
            self.game_state.set_game_state("menu")
    
    def handle_analysis_click(self, pos):
        """Handle a click during analysis mode."""
        buttons = self.ui_manager.buttons
        
        if buttons["back"].is_clicked(pos):
            self.game_state.go_back()
        elif buttons["forward"].is_clicked(pos):
            self.game_state.go_forward()
        elif buttons["evaluate"].is_clicked(pos):
            self.game_state.toggle_evaluation()
            self.handle_evaluation_toggle()
        elif buttons["best move"].is_clicked(pos) and self.game_state.evaluation_mode:
            self.game_state.toggle_best_move()
        elif buttons["menu"].is_clicked(pos):
            self.game_state.set_game_state("menu")
        elif buttons["back to end"].is_clicked(pos):
            self.game_state.set_game_state("game_over")
    
    def handle_evaluation_toggle(self):
        """Handle toggling evaluation mode on/off."""
        if self.game_state.evaluation_mode:
            # Start evaluation
            self.engine_manager.start_evaluation(self.game_state.board, None)  # Using None for callback; it's handled in main.py
        else:
            # Stop evaluation
            self.engine_manager.stop_evaluation()
    
    def make_ai_move(self):
        """Make a move for the AI."""
        move = self.engine_manager.get_best_move(self.game_state.board, self.game_state.difficulty)
        if move:
            self.game_state.make_move(move) 