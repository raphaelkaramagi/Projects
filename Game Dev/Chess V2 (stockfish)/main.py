import pygame
import sys
import chess
from config import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE

from game_state import GameState
from engine_manager import EngineManager
from board_renderer import BoardRenderer
from ui_elements import UIManager
from input_handler import InputHandler

class ChessGame:
    """Main game class that ties all components together."""
    
    def __init__(self): 
        """Initialize the chess game."""
        # Initialize Pygame
        pygame.init()
        
        # Set up the display
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Python Chess Game")
        self.clock = pygame.time.Clock()
        
        # Initialize game components
        self.game_state = GameState()
        self.engine_manager = EngineManager()
        self.board_renderer = BoardRenderer(self.screen)
        self.ui_manager = UIManager(self.screen)
        self.input_handler = InputHandler(self.game_state, self.engine_manager, self.ui_manager)
        
        # Set up callbacks for state and position changes
        self.game_state.set_state_change_callback(self.on_state_change)
        self.game_state.set_position_change_callback(self.on_position_change)
    
    def on_state_change(self, old_state, new_state):
        """Handle state changes in the game."""
        # Stop evaluation when leaving a state that might have it active
        if old_state in ["playing", "analysis"] and new_state not in ["playing", "analysis"]:
            if self.game_state.evaluation_mode:
                self.game_state.evaluation_mode = False
                self.engine_manager.stop_evaluation()
        
        # Reset engine state when going to menu or starting new games
        if new_state == "menu" or (new_state == "playing" and old_state != "difficulty"):
            self.engine_manager.reset_evaluation_state()
        
        # Start evaluation when entering analysis mode
        if new_state == "analysis" and not self.game_state.evaluation_mode:
            self.game_state.evaluation_mode = True
            self.engine_manager.start_evaluation(self.game_state.board, self._on_evaluation_update)
    
    def on_position_change(self, board):
        """Handle position changes during navigation."""
        # Update evaluation for the new position if evaluation is active
        if self.game_state.evaluation_mode:
            self.engine_manager.update_evaluation_position(board)
    
    def handle_promotion_event(self, event):
        """Handle events during promotion dialog."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            
            # Get dialog and button positions
            dialog_x, dialog_y, buttons = self.ui_manager.show_promotion_dialog()
            
            # Check if any button was clicked
            for button_rect, piece in buttons:
                # Adjust mouse position relative to dialog
                rel_x = mouse_pos[0] - dialog_x
                rel_y = mouse_pos[1] - dialog_y
                
                if button_rect.collidepoint(rel_x, rel_y):
                    # Create promoted move
                    move = self.game_state.pending_promotion['move']
                    promoted_move = chess.Move(move.from_square, move.to_square, promotion=piece)
                    
                    # Clear promotion state
                    self.game_state.pending_promotion = None
                    self.game_state.selected_square = None
                    self.game_state.legal_moves_squares = []
                    
                    # Make the move
                    self.game_state.make_move(promoted_move)
                    
                    # Make AI move if appropriate
                    if (self.game_state.difficulty and 
                        self.game_state.game_state == "playing" and
                        self.game_state.board.turn != self.game_state.player_color):
                        self.input_handler.make_ai_move()
                    
                    break
    
    def _on_evaluation_update(self, best_move, evaluation, pv_line, mate_in=None):
        """Callback for evaluation updates."""
        # Store updated evaluation data - no lock needed since we're already in the locked section
        self.engine_manager.best_move = best_move
        self.engine_manager.evaluation = evaluation
        self.engine_manager.pv_line = pv_line
        self.engine_manager.mate_in = mate_in
    
    def run(self):
        """Run the main game loop."""
        running = True
        
        # Override the input handler's evaluation toggle to use our callback
        original_handle_evaluation_toggle = self.input_handler.handle_evaluation_toggle
        
        def new_handle_evaluation_toggle():
            if self.game_state.evaluation_mode:
                self.engine_manager.start_evaluation(self.game_state.board, self._on_evaluation_update)
            else:
                self.engine_manager.stop_evaluation()
        
        self.input_handler.handle_evaluation_toggle = new_handle_evaluation_toggle
        
        while running:
            # Process events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    continue
                
                # Handle promotion dialog specially
                if self.game_state.pending_promotion:
                    self.handle_promotion_event(event)
                else:
                    if not self.input_handler.handle_event(event):
                        running = False
            
            # Clear the screen
            self.screen.fill(WHITE)
            
            # Render the current state
            if self.game_state.game_state == "menu":
                self.ui_manager.draw_menu()
            elif self.game_state.game_state == "color_select":
                self.ui_manager.draw_color_menu()
            elif self.game_state.game_state == "difficulty":
                self.ui_manager.draw_difficulty_menu()
            elif self.game_state.game_state in ["playing", "analysis"]:
                self.draw_game()
            elif self.game_state.game_state == "game_over":
                self.draw_game()
                self.ui_manager.draw_game_over(self.game_state.result)
            
            # Draw promotion dialog if active
            if self.game_state.pending_promotion:
                self.ui_manager.show_promotion_dialog()
            
            # Update the display
            pygame.display.flip()
            
            # Cap the frame rate
            self.clock.tick(60)
        
        # Clean up
        self.quit_game()
    
    def draw_game(self):
        """Draw the game board and UI elements."""
        # Draw the board and pieces
        self.board_renderer.draw_board()
        self.board_renderer.draw_pieces(self.game_state.board)
        
        # Highlight the last move
        if self.game_state.last_move:
            self.board_renderer.highlight_last_move(self.game_state.last_move)
        
        # Highlight the selected square and legal moves
        if self.game_state.selected_square:
            self.board_renderer.highlight_square(self.game_state.selected_square)
        
        if self.game_state.legal_moves_squares:
            self.board_renderer.highlight_legal_moves(self.game_state.legal_moves_squares)
        
        # Draw UI elements
        self.ui_manager.draw_game_controls(
            self.game_state.evaluation_mode,
            self.game_state.show_best_move,
            self.game_state
        )
        
        # Draw game statistics
        self.ui_manager.draw_game_stats(
            self.game_state.game_count,
            self.game_state.difficulty
        )
        
        # Draw evaluation elements if evaluation mode is active
        if self.game_state.evaluation_mode:
            with self.engine_manager.evaluation_lock:
                self.ui_manager.draw_evaluation_bar(
                    self.engine_manager.evaluation, 
                    self.engine_manager.mate_in,
                    self.game_state.board.turn
                )
                
                # Show best move if requested
                if self.game_state.show_best_move:
                    if self.engine_manager.best_move and self.engine_manager.best_move in self.game_state.board.legal_moves:
                        self.board_renderer.draw_best_move(self.engine_manager.best_move)
                    
                    self.ui_manager.draw_evaluation_info(
                        self.engine_manager.best_move,
                        self.game_state.board,
                        self.engine_manager.pv_line
                    )
        
        # In analysis mode, show the move counter
        if self.game_state.game_state == "analysis":
            self.ui_manager.draw_move_counter(
                self.game_state.current_move_index,
                len(self.game_state.move_history)
            )
    
    def quit_game(self):
        """Clean up resources and quit the game."""
        self.engine_manager.quit()
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = ChessGame()
    game.run() 