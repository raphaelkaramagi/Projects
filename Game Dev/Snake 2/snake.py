import pygame
import random
from enum import Enum
from collections import namedtuple
import os

# Initialize Pygame
pygame.init()

# Define colors
WHITE = (255, 255, 255)
RED = (200, 0, 0)
BLUE1 = (0, 0, 255)
BLUE2 = (0, 100, 255)
BLACK = (0, 0, 0)

# Game settings
BLOCK_SIZE = 20
SPEED = 10

# Add new settings
FULLSCREEN = False
HIGHSCORE_FILE = "highscore.txt"

# Direction enum
class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4

# Point named tuple
Point = namedtuple('Point', 'x, y')

class SnakeGame:
    def __init__(self, w=640, h=480):
        self.w = w
        self.h = h
        
        # Initialize display
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption('Snake')
        self.clock = pygame.time.Clock()
        
        # Initialize game state
        self.reset()
        self.original_w = w
        self.original_h = h
        self.fullscreen = FULLSCREEN
        self.highscore = self.load_highscore()
        self.in_menu = True

    def reset(self):
        # Initial snake position and direction
        self.direction = Direction.RIGHT
        self.head = Point(self.w/2, self.h/2)
        self.snake = [
            self.head,
            Point(self.head.x-BLOCK_SIZE, self.head.y),
            Point(self.head.x-(2*BLOCK_SIZE), self.head.y)
        ]
        
        self.score = 0
        self.food = None
        self._place_food()

    def _place_food(self):
        x = random.randint(0, (self.w-BLOCK_SIZE)//BLOCK_SIZE)*BLOCK_SIZE
        y = random.randint(0, (self.h-BLOCK_SIZE)//BLOCK_SIZE)*BLOCK_SIZE
        self.food = Point(x, y)
        if self.food in self.snake:
            self._place_food()

    def load_highscore(self):
        try:
            with open(HIGHSCORE_FILE, 'r') as f:
                return int(f.read())
        except:
            return 0

    def save_highscore(self):
        with open(HIGHSCORE_FILE, 'w') as f:
            f.write(str(max(self.score, self.highscore)))

    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            self.w = pygame.display.Info().current_w
            self.h = pygame.display.Info().current_h
            self.display = pygame.display.set_mode((self.w, self.h), pygame.FULLSCREEN)
        else:
            self.w = self.original_w
            self.h = self.original_h
            self.display = pygame.display.set_mode((self.w, self.h))
        self.reset()

    def show_menu(self):
        self.display.fill(BLACK)
        font = pygame.font.Font(None, 74)
        title = font.render('Snake Game', True, WHITE)
        start = font.render('Press SPACE to Start', True, WHITE)
        highscore = font.render(f'Highscore: {self.highscore}', True, WHITE)
        
        self.display.blit(title, [self.w/2 - title.get_width()/2, self.h/3])
        self.display.blit(start, [self.w/2 - start.get_width()/2, self.h/2])
        self.display.blit(highscore, [self.w/2 - highscore.get_width()/2, 2*self.h/3])
        pygame.display.flip()

    def play_step(self):
        # Handle menu state
        if self.in_menu:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.in_menu = False
                        self.reset()
                    elif event.key == pygame.K_f:
                        self.toggle_fullscreen()
            self.show_menu()
            return False, self.score

        # Regular game input handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_f:
                    self.toggle_fullscreen()
                if event.key == pygame.K_LEFT and self.direction != Direction.RIGHT:
                    self.direction = Direction.LEFT
                elif event.key == pygame.K_RIGHT and self.direction != Direction.LEFT:
                    self.direction = Direction.RIGHT
                elif event.key == pygame.K_UP and self.direction != Direction.DOWN:
                    self.direction = Direction.UP
                elif event.key == pygame.K_DOWN and self.direction != Direction.UP:
                    self.direction = Direction.DOWN

        # 2. Move
        self._move(self.direction)
        self.snake.insert(0, self.head)

        # 3. Check if game over
        game_over = False
        if self._is_collision():
            game_over = True
            self.save_highscore()
            self.in_menu = True
            return game_over, self.score

        # 4. Place new food or move
        if self.head == self.food:
            self.score += 1
            self._place_food()
        else:
            self.snake.pop()

        # 5. Update UI and clock
        self._update_ui()
        self.clock.tick(SPEED)

        # 6. Return game over and score
        return game_over, self.score

    def _is_collision(self):
        # Wrap around instead of collision with boundaries
        if self.head.x >= self.w:
            self.head = Point(0, self.head.y)
        elif self.head.x < 0:
            self.head = Point(self.w - BLOCK_SIZE, self.head.y)
        elif self.head.y >= self.h:
            self.head = Point(self.head.x, 0)
        elif self.head.y < 0:
            self.head = Point(self.head.x, self.h - BLOCK_SIZE)
        
        # Only check collision with self
        if self.head in self.snake[1:]:
            return True
        return False

    def _update_ui(self):
        self.display.fill(BLACK)

        # Draw snake
        for pt in self.snake:
            pygame.draw.rect(self.display, BLUE1, pygame.Rect(pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE))
            pygame.draw.rect(self.display, BLUE2, pygame.Rect(pt.x+4, pt.y+4, 12, 12))

        # Draw food
        pygame.draw.rect(self.display, RED, pygame.Rect(self.food.x, self.food.y, BLOCK_SIZE, BLOCK_SIZE))

        # Draw score
        font = pygame.font.Font(None, 36)
        text = font.render(f"Score: {self.score}", True, WHITE)
        self.display.blit(text, [0, 0])
        pygame.display.flip()

    def _move(self, direction):
        x = self.head.x
        y = self.head.y
        if direction == Direction.RIGHT:
            x += BLOCK_SIZE
        elif direction == Direction.LEFT:
            x -= BLOCK_SIZE
        elif direction == Direction.DOWN:
            y += BLOCK_SIZE
        elif direction == Direction.UP:
            y -= BLOCK_SIZE
        self.head = Point(x, y)

if __name__ == '__main__':
    game = SnakeGame()
    
    # Game loop
    while True:
        game_over, score = game.play_step()
        
        if game_over:
            continue  # Instead of breaking, continue to show menu
    
    pygame.quit()
