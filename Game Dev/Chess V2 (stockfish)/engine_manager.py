import chess
import chess.engine
import threading
import concurrent.futures
from config import STOCKFISH_PATH, ENGINE_THREADS, ENGINE_HASH, DIFFICULTY_SETTINGS, EVAL_TIME, EVAL_DEPTH, EVAL_PV_LINE_LENGTH

class EngineManager:
    """Class to manage interactions with the chess engine (Stockfish)."""
    
    def __init__(self):
        """Initialize the engine manager."""
        self.engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)
        self.engine.configure({"Threads": ENGINE_THREADS, "Hash": ENGINE_HASH})
        self.stop_evaluation_event = threading.Event()
        self.evaluation_lock = threading.Lock()
        self.evaluation_thread = None
        self.evaluation = None
        self.best_move = None
        self.pv_line = []
        self.mate_in = None
        self._current_callback = None
        self._current_board = None
    
    def set_difficulty(self, difficulty):
        """Set the difficulty level for the engine."""
        if difficulty in DIFFICULTY_SETTINGS:
            settings = DIFFICULTY_SETTINGS[difficulty]
            self.engine.configure({"Skill Level": settings["skill_level"]})
    
    def get_best_move(self, board, difficulty):
        """Get the best move from the engine for the given board position."""
        # Temporarily stop evaluation to avoid engine conflicts
        was_evaluating = self.evaluation_thread and self.evaluation_thread.is_alive()
        if was_evaluating:
            self.stop_evaluation()
        
        try:
            settings = DIFFICULTY_SETTINGS[difficulty]
            result = self.engine.play(
                board, 
                chess.engine.Limit(
                    time=settings["time"], 
                    depth=settings["depth"]
                )
            )
            move = result.move
        except concurrent.futures.CancelledError:
            print("AI move was cancelled")
            move = None
        except Exception as e:
            print(f"Error in AI move: {str(e)}")
            move = None
        
        # Restart evaluation if it was running before
        if was_evaluating:
            # Use the updated board position after the move
            updated_board = board.copy()
            if move:
                updated_board.push(move)
            self.start_evaluation(updated_board, self._current_callback)
        
        return move
    
    def start_evaluation(self, board, callback):
        """Start continuous evaluation of the position."""
        # Stop any existing evaluation
        self.stop_evaluation()
        
        # Store current state for potential restart
        self._current_callback = callback
        self._current_board = board.copy()
        
        self.stop_evaluation_event.clear()
        self.evaluation_thread = threading.Thread(
            target=self._evaluation_worker, 
            args=(board, callback)
        )
        self.evaluation_thread.start()
    
    def stop_evaluation(self):
        """Stop the continuous evaluation."""
        if self.evaluation_thread and self.evaluation_thread.is_alive():
            self.stop_evaluation_event.set()
            self.evaluation_thread.join()
    
    def update_evaluation_position(self, board):
        """Update the evaluation for a new board position while keeping evaluation active."""
        if self.evaluation_thread and self.evaluation_thread.is_alive():
            # Restart evaluation with new position
            self.start_evaluation(board, self._current_callback)
    
    def reset_evaluation_state(self):
        """Reset evaluation state completely - useful when starting new games."""
        self.stop_evaluation()
        with self.evaluation_lock:
            self.evaluation = None
            self.best_move = None
            self.pv_line = []
            self.mate_in = None
        self._current_callback = None
        self._current_board = None
    
    def _evaluation_worker(self, board, callback):
        """Worker thread for continuous position evaluation."""
        while not self.stop_evaluation_event.is_set():
            try:
                info = self.engine.analyse(
                    board, 
                    chess.engine.Limit(time=EVAL_TIME, depth=EVAL_DEPTH)
                )
                
                with self.evaluation_lock:
                    # Extract best move
                    pv = info.get("pv", [])
                    best_move = pv[0] if pv and pv[0] in board.legal_moves else None
                    
                    # Extract evaluation score
                    score = info.get("score")
                    evaluation = None
                    mate_in = None
                    
                    if score:
                        try:
                            # Get score from white's perspective (consistent display)
                            evaluation = score.white().score()
                        except (ValueError, TypeError):
                            # Handle mate scores
                            if score.is_mate():
                                mate_moves = score.white().mate()
                                if mate_moves is not None:
                                    mate_in = abs(mate_moves)
                                    # Use large values for mate, preserving sign
                                    evaluation = 30000 if mate_moves > 0 else -30000
                                else:
                                    evaluation = 0  # Fallback for unclear mate
                            else:
                                evaluation = 0  # Fallback for other score types
                    else:
                        evaluation = 0  # Never leave evaluation as None
                    
                    # Generate PV line
                    pv_board = board.copy()
                    pv_line = []
                    for move in pv[:EVAL_PV_LINE_LENGTH]:
                        if pv_board.is_legal(move):
                            pv_line.append(pv_board.san(move))
                            pv_board.push(move)
                        else:
                            break
                    
                    # Update evaluation data
                    self.best_move = best_move
                    self.evaluation = evaluation
                    self.pv_line = pv_line
                    self.mate_in = mate_in
                    
                    # Call the callback with updated data
                    if callback:
                        callback(best_move, evaluation, pv_line, mate_in)
                        
            except concurrent.futures.CancelledError:
                print("Evaluation was cancelled")
                break
            except Exception as e:
                print(f"Error in evaluation: {str(e)}")
            
            self.stop_evaluation_event.wait(0.1)  # Wait for 100ms or until stop_evaluation is set
    
    def quit(self):
        """Clean up the engine resources."""
        self.stop_evaluation_event.set()
        if self.evaluation_thread and self.evaluation_thread.is_alive():
            self.evaluation_thread.join()
        if self.engine:
            self.engine.quit() 