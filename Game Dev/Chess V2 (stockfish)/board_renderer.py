import pygame
import chess
from config import SQUARE_SIZE, BOARD_SIZE, LIGHT_SQUARE, DARK_SQUARE, HIGHLIGHT, BLACK, BEST_MOVE_COLOR
from utils import load_pieces, square_to_coords, get_square_center

class BoardRenderer:
    """Handles rendering of the chess board, pieces, and move highlights."""
    
    def __init__(self, screen):
        """Initialize the board renderer."""
        self.screen = screen
        self.pieces = load_pieces()
        self.font = pygame.font.Font(None, 24)
    
    def draw_board(self):
        """Draw the chess board squares and labels."""
        # Draw squares
        for row in range(8):
            for col in range(8):
                color = LIGHT_SQUARE if (row + col) % 2 == 0 else DARK_SQUARE
                pygame.draw.rect(
                    self.screen, 
                    color, 
                    (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
                )
        
        # Draw board labels
        for i in range(8):
            file_label = self.font.render(chess.FILE_NAMES[i], True, BLACK)
            rank_label = self.font.render(str(8 - i), True, BLACK)
            self.screen.blit(file_label, (i * SQUARE_SIZE + 5, BOARD_SIZE + 5))
            self.screen.blit(rank_label, (BOARD_SIZE + 5, i * SQUARE_SIZE + 5))
    
    def draw_pieces(self, board):
        """Draw the chess pieces on the board."""
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece:
                x, y = square_to_coords(square)
                self.screen.blit(self.pieces[piece.symbol()], (x, y))
    
    def highlight_square(self, square):
        """Highlight a specific square."""
        x, y = square_to_coords(square)
        pygame.draw.rect(self.screen, HIGHLIGHT, (x, y, SQUARE_SIZE, SQUARE_SIZE), 3)
    
    def highlight_last_move(self, move):
        """Highlight the last move made on the board."""
        if move:
            self.highlight_square(move.from_square)
            self.highlight_square(move.to_square)
    
    def highlight_legal_moves(self, squares):
        """Highlight squares for legal moves."""
        for square in squares:
            x, y = square_to_coords(square)
            pygame.draw.circle(
                self.screen, 
                HIGHLIGHT, 
                (x + SQUARE_SIZE // 2, y + SQUARE_SIZE // 2), 
                SQUARE_SIZE // 6
            )
    
    def draw_best_move(self, best_move):
        """Draw an arrow indicating the best move."""
        if best_move:
            from_x, from_y = get_square_center(best_move.from_square)
            to_x, to_y = get_square_center(best_move.to_square)
            
            # Draw the arrow line
            pygame.draw.line(self.screen, BEST_MOVE_COLOR, (from_x, from_y), (to_x, to_y), 3)
            
            # Draw circles at the start and end points
            pygame.draw.circle(self.screen, BEST_MOVE_COLOR, (from_x, from_y), 10)
            pygame.draw.circle(self.screen, (255, 0, 0), (to_x, to_y), 10) 