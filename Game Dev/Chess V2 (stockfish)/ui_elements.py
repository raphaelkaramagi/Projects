import pygame
import chess
from config import BOARD_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, BLACK, GREY

class Button:
    """A simple button class for UI interaction."""
    
    def __init__(self, rect, text, font):
        """Initialize a button with a rectangle, text, and font."""
        self.rect = rect
        self.text = text
        self.font = font
        self.active = True
    
    def draw(self, screen, color=GREY, highlight=False):
        """Draw the button on the screen."""
        if not self.active:
            return
        
        # Draw button rectangle
        pygame.draw.rect(screen, color, self.rect)
        
        # Draw button text
        text_surf = self.font.render(self.text, True, BLACK)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)
        
        # Draw highlight border if necessary
        if highlight:
            pygame.draw.rect(screen, BLACK, self.rect, 2)
    
    def is_clicked(self, pos):
        """Check if the button was clicked."""
        return self.active and self.rect.collidepoint(pos)


class UIManager:
    """Manages all UI elements for the chess game."""
    
    def __init__(self, screen):
        """Initialize the UI manager."""
        self.screen = screen
        self.font = pygame.font.Font(None, 24)
        self.title_font = pygame.font.Font(None, 36)
        self.large_font = pygame.font.Font(None, 48)
        self.buttons = {}
        self.create_buttons()
    
    def create_buttons(self):
        """Create all the buttons needed for the game."""
        button_width = 120
        button_height = 40
        button_margin = 10
        start_x = BOARD_SIZE + 20
        start_y = 20
        
        # Game control buttons
        button_texts = ["Resign", "Draw", "Menu", "Back", "Forward", "Evaluate", "Best Move", "Decline Draw"]
        for i, text in enumerate(button_texts):
            x = start_x + (i % 2) * (button_width + button_margin)
            y = start_y + (i // 2) * (button_height + button_margin)
            self.buttons[text.lower()] = Button(
                pygame.Rect(x, y, button_width, button_height),
                text,
                self.font
            )
        
        # Place "Best Move" button at the bottom
        self.buttons["best move"].rect = pygame.Rect(BOARD_SIZE + 20, SCREEN_HEIGHT - 150, button_width, button_height)
        
        # Menu buttons
        menu_buttons = ["Single Player", "Two Player", "Quit"]
        for i, text in enumerate(menu_buttons):
            self.buttons[text.lower()] = Button(
                pygame.Rect(SCREEN_WIDTH // 2 - 100, 150 + i * 60, 200, 50),
                text,
                self.title_font
            )
        
        # Color selection buttons
        color_buttons = ["Play as White", "Play as Black", "Back to Menu"]
        for i, text in enumerate(color_buttons):
            self.buttons[text.lower()] = Button(
                pygame.Rect(SCREEN_WIDTH // 2 - 100, 150 + i * 60, 200, 50),
                text,
                self.title_font
            )
        
        # Difficulty buttons
        difficulty_buttons = ["Easy", "Medium", "Hard", "Back to Menu"]
        for i, text in enumerate(difficulty_buttons):
            self.buttons[text.lower()] = Button(
                pygame.Rect(SCREEN_WIDTH // 2 - 100, 150 + i * 60, 200, 50),
                text,
                self.title_font
            )
        
        # Game over buttons
        game_over_buttons = ["Analyze", "Play Again", "Main Menu"]
        for i, text in enumerate(game_over_buttons):
            self.buttons[text.lower()] = Button(
                pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 50 + i * 60, 200, 50),
                text,
                self.title_font
            )
        
        # Analysis button
        self.buttons["back to end"] = Button(
            pygame.Rect(SCREEN_WIDTH - 180, SCREEN_HEIGHT - 50, 160, 40),
            "Back to End Screen",
            self.font
        )
    
    def draw_menu(self):
        """Draw the main menu screen."""
        self.screen.fill(WHITE)
        
        # Draw title
        title = self.title_font.render("Python Chess Game", True, BLACK)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 50))
        
        # Draw menu buttons
        for button_name in ["single player", "two player", "quit"]:
            self.buttons[button_name].draw(self.screen)
    
    def draw_color_menu(self):
        """Draw the color selection menu."""
        self.screen.fill(WHITE)
        
        # Draw title
        title = self.title_font.render("Choose Your Color", True, BLACK)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 50))
        
        # Draw color buttons
        for button_name in ["play as white", "play as black", "back to menu"]:
            self.buttons[button_name].draw(self.screen)
    
    def draw_difficulty_menu(self):
        """Draw the difficulty selection menu."""
        self.screen.fill(WHITE)
        
        # Draw title
        title = self.title_font.render("Select Difficulty", True, BLACK)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 50))
        
        # Draw difficulty buttons
        for button_name in ["easy", "medium", "hard", "back to menu"]:
            self.buttons[button_name].draw(self.screen)
    
    def draw_game_over(self, result):
        """Draw the game over overlay with the result and options."""
        # Create semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(WHITE)
        self.screen.blit(overlay, (0, 0))
        
        # Draw result text
        text_surf = self.large_font.render(result, True, BLACK)
        text_rect = text_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(text_surf, text_rect)
        
        # Draw game over buttons
        for button_name in ["analyze", "play again", "main menu"]:
            self.buttons[button_name].draw(self.screen)
    
    def draw_game_controls(self, evaluation_mode, show_best_move, game_state=None):
        """Draw the game control buttons."""
        # Update button states
        self.buttons["evaluate"].active = True
        self.buttons["best move"].active = evaluation_mode
        
        # Handle draw request state for two-player games
        draw_requested = game_state and hasattr(game_state, 'draw_requested') and game_state.draw_requested
        is_multiplayer = game_state and game_state.difficulty is None
        
        self.buttons["decline draw"].active = draw_requested and is_multiplayer
        
        # Draw buttons with appropriate highlighting
        for name, button in self.buttons.items():
            if name in ["resign", "draw", "menu", "back", "forward", "evaluate", "best move", "decline draw"]:
                color = GREY
                # Highlight active evaluation button
                if name == "evaluate" and evaluation_mode:
                    color = (0, 255, 0)
                # Highlight active best move button
                elif name == "best move" and show_best_move:
                    color = (0, 255, 0)
                # Highlight draw button when draw is requested
                elif name == "draw" and draw_requested:
                    color = (255, 255, 0)  # Yellow to indicate pending request
                    button.text = "Accept Draw" if draw_requested else "Draw"
                elif name == "decline draw" and draw_requested:
                    color = (255, 200, 200)  # Light red for decline
                
                # Reset draw button text when no request pending
                if name == "draw" and not draw_requested:
                    button.text = "Draw"
                
                button.draw(self.screen, color)
        
        # Draw draw request notification
        if draw_requested and is_multiplayer:
            text_surf = self.font.render("Draw requested! Accept or Decline?", True, BLACK)
            self.screen.blit(text_surf, (BOARD_SIZE + 20, SCREEN_HEIGHT - 200))
    
    def draw_evaluation_bar(self, evaluation, mate_in=None, current_turn=True):
        """Draw the evaluation bar showing the current position evaluation."""
        import chess
        
        bar_height = 300
        bar_width = 20
        bar_x = SCREEN_WIDTH - 40
        bar_y = (SCREEN_HEIGHT - bar_height) // 2
        
        # Draw background
        pygame.draw.rect(self.screen, WHITE, (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(self.screen, BLACK, (bar_x, bar_y, bar_width, bar_height), 2)
        
        # Always have some evaluation to show
        if evaluation is None:
            evaluation = 0
        
        # Calculate evaluation height (normalized between 0 and bar_height)
        if abs(evaluation) > 10000:  # Mate score
            eval_height = bar_height if evaluation > 0 else 0
        else:
            # Clamp evaluation for display (-10.00 to +10.00 range)
            clamped_eval = max(-1000, min(1000, evaluation))
            eval_height = min(max(0, (clamped_eval + 1000) / 2000 * bar_height), bar_height)
        
        # Draw the evaluation portion
        pygame.draw.rect(
            self.screen, 
            BLACK, 
            (bar_x, bar_y + bar_height - eval_height, bar_width, eval_height)
        )
        
        # Draw evaluation text
        if mate_in is not None and abs(evaluation) > 10000:
            # Show proper mate notation
            if evaluation > 0:
                eval_text = f"Mate in {mate_in}"
            else:
                eval_text = f"Mate in {mate_in}"
        elif abs(evaluation) > 1000:
            # Large advantage but not mate
            eval_text = f"{evaluation / 100:+.1f}"
        else:
            # Normal evaluation
            eval_text = f"{evaluation / 100:+.2f}"
        
        text_surf = self.font.render(eval_text, True, BLACK)
        self.screen.blit(text_surf, (bar_x - 60, bar_y + bar_height // 2))
    
    def draw_evaluation_info(self, best_move, board, pv_line):
        """Draw information about the best move and PV line."""
        if best_move:
            try:
                # Get best move text
                if best_move in board.legal_moves:
                    best_move_text = f"Best: {board.san(best_move)}"
                else:
                    best_move_text = f"Best: {best_move.uci()} (not applicable)"
                
                # Draw best move text
                text_surf = self.font.render(best_move_text, True, BLACK)
                self.screen.blit(text_surf, (BOARD_SIZE + 20, SCREEN_HEIGHT - 90))
                
            except Exception as e:
                # Handle any errors
                error_text = f"Best move error: {str(e)}"
                text_surf = self.font.render(error_text, True, BLACK)
                self.screen.blit(text_surf, (BOARD_SIZE + 20, SCREEN_HEIGHT - 90))
        
        # Draw PV line
        if pv_line:
            pv_text = "Line: " + " ".join(pv_line)
            text_surf = self.font.render(pv_text, True, BLACK)
            self.screen.blit(text_surf, (BOARD_SIZE + 20, SCREEN_HEIGHT - 60))
        else:
            text_surf = self.font.render("No valid line available", True, BLACK)
            self.screen.blit(text_surf, (BOARD_SIZE + 20, SCREEN_HEIGHT - 60))
    
    def draw_game_stats(self, game_count, difficulty):
        """Draw game statistics (wins/losses/draws)."""
        opponent = 'Player 2' if difficulty is None else 'Stockfish'
        count_text = f"Player 1: {game_count['player']} {opponent}: {game_count['stockfish']} Draw: {game_count['draw']}"
        count_surf = self.font.render(count_text, True, BLACK)
        self.screen.blit(count_surf, (BOARD_SIZE + 20, SCREEN_HEIGHT - 30))
    
    def draw_move_counter(self, current_index, total_moves):
        """Draw the move counter for analysis mode."""
        move_text = f"Move: {current_index + 1}/{total_moves}"
        text_surf = self.font.render(move_text, True, BLACK)
        self.screen.blit(text_surf, (BOARD_SIZE + 20, SCREEN_HEIGHT - 120))
    
    def show_promotion_dialog(self):
        """Show dialog for pawn promotion piece selection."""
        dialog_width, dialog_height = 200, 250
        dialog_x = (SCREEN_WIDTH - dialog_width) // 2
        dialog_y = (SCREEN_HEIGHT - dialog_height) // 2
        
        # Create dialog surface
        dialog = pygame.Surface((dialog_width, dialog_height))
        dialog.fill(WHITE)
        pygame.draw.rect(dialog, BLACK, (0, 0, dialog_width, dialog_height), 2)
        
        # Add title
        text = self.font.render("Choose promotion:", True, BLACK)
        dialog.blit(text, (10, 10))
        
        # Create buttons for each piece option
        pieces = [chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT]
        piece_names = ["Queen", "Rook", "Bishop", "Knight"]
        buttons = []
        
        for i, (piece, name) in enumerate(zip(pieces, piece_names)):
            button = pygame.Rect(50, 50 + i * 50, 100, 40)
            pygame.draw.rect(dialog, GREY, button)
            text = self.font.render(name, True, BLACK)
            text_rect = text.get_rect(center=button.center)
            dialog.blit(text, text_rect)
            buttons.append((button, piece))
        
        # Display the dialog
        self.screen.blit(dialog, (dialog_x, dialog_y))
        pygame.display.flip()
        
        # Return the dialog position and buttons for later handling
        return dialog_x, dialog_y, buttons 