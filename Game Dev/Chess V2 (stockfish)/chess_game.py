"""
Chess Game Entry Point

This file serves as a backward-compatible entry point to the chess game.
The actual implementation has been refactored into modular components
for better organization and maintainability.
"""

from main import ChessGame

if __name__ == "__main__":
    # Create and run the game
    game = ChessGame()
    game.run()