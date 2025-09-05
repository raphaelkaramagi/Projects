# Python Chess Game

A fully functional chess game written in Python using Pygame and the Stockfish chess engine.

## Features

- Single player mode with adjustable difficulty (Easy, Medium, Hard)
- Two player mode
- Position evaluation with Stockfish engine
- Best move indicators
- Move history navigation
- Game analysis after completion
- Automatic detection of game-ending conditions
- Pawn promotion
- Game statistics tracking

## Requirements

- Python 3.x
- Pygame
- python-chess
- Stockfish chess engine

## Installation

1. Ensure you have Python installed on your system.
2. Install the required packages:
   ```
   pip install pygame python-chess
   ```
3. Download Stockfish from the [official website](https://stockfishchess.org/download/) and place the executable in the project directory or update the `STOCKFISH_PATH` in `config.py`.

## Project Structure

The project has been organized into modular components:

- **main.py**: The entry point of the application that ties everything together
- **config.py**: Contains constants and configuration settings
- **utils.py**: Utility functions for common operations
- **game_state.py**: Manages the game state and rules
- **engine_manager.py**: Handles interactions with the Stockfish engine
- **board_renderer.py**: Responsible for rendering the chess board and pieces
- **ui_elements.py**: Manages the user interface elements and rendering
- **input_handler.py**: Processes user input and events

## How to Run

Simply execute the main.py file:

```
python main.py
```

## Controls

- **Mouse**: Click to select and move pieces
- **UI Buttons**:
  - **Resign**: Forfeit the current game
  - **Draw**: Offer a draw (in multiplayer mode)
  - **Menu**: Return to the main menu
  - **Back/Forward**: Navigate through move history
  - **Evaluate**: Toggle the engine evaluation
  - **Best Move**: Toggle showing the best move

## Game Modes

- **Single Player**: Play against Stockfish with three difficulty levels
- **Two Player**: Play against another human on the same computer

## Analysis Mode

After a game ends, you can analyze the game by selecting "Analyze" on the game over screen. In analysis mode, you can:

- Navigate through the moves using the Back/Forward buttons
- See engine evaluations of positions
- View the best moves at each position
- See the principal variation (sequence of best moves)

## License

This project is open-source software available under the MIT License.