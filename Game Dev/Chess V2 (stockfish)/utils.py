import pygame
import chess
from config import SQUARE_SIZE

def load_pieces():
    """Load chess piece images and scale them to the appropriate size."""
    pieces = {}
    for color in ['w', 'b']:
        for piece in ['p', 'n', 'b', 'r', 'q', 'k']:
            image = pygame.image.load(f"assets/{color}{piece}.png")
            if color == 'w':
                piece = piece.upper()
            pieces[piece] = pygame.transform.scale(image, (SQUARE_SIZE, SQUARE_SIZE))
    return pieces

def square_to_coords(square):
    """Convert a chess square (0-63) to screen coordinates."""
    file = chess.square_file(square)
    rank = 7 - chess.square_rank(square)
    return file * SQUARE_SIZE, rank * SQUARE_SIZE

def coords_to_square(x, y):
    """Convert screen coordinates to a chess square (0-63)."""
    file = x // SQUARE_SIZE
    rank = 7 - (y // SQUARE_SIZE)
    return chess.square(file, rank)

def get_square_center(square):
    """Get the center coordinates of a chess square."""
    x, y = square_to_coords(square)
    return x + SQUARE_SIZE // 2, y + SQUARE_SIZE // 2 