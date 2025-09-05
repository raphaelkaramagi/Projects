import pygame
import random

# Initialize Pygame
pygame.init()

# Game window settings
WIDTH, HEIGHT = 800, 600
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Geometry Dash Clone")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# Game settings
FPS = 60
GRAVITY = 0.8
JUMP_FORCE = -18
GROUND = HEIGHT - 50
OBSTACLE_SPEED = 10

# Player class
class Player:
    def __init__(self):
        self.rect = pygame.Rect(100, GROUND - 30, 30, 30)
        self.velocity = 0
        self.is_jumping = False

    def jump(self):
        if not self.is_jumping:
            self.velocity = JUMP_FORCE
            self.is_jumping = True

    def update(self):
        self.velocity += GRAVITY
        self.rect.y += self.velocity

        # Ground collision
        if self.rect.bottom >= GROUND:
            self.rect.bottom = GROUND
            self.velocity = 0
            self.is_jumping = False

# Obstacle class
class Obstacle:
    def __init__(self, x):
        self.rect = pygame.Rect(x, GROUND - 40, 40, 40)
        self.passed = False

    def update(self):
        self.rect.x -= OBSTACLE_SPEED

# Game manager
class Game:
    def __init__(self):
        self.player = Player()
        self.obstacles = []
        self.score = 0
        self.spawn_timer = 0
        self.game_over = False

    def spawn_obstacle(self):
        if random.randint(0, 100) < 3 and len(self.obstacles) < 3:
            self.obstacles.append(Obstacle(WIDTH + 100))

    def check_collision(self):
        for obstacle in self.obstacles:
            if self.player.rect.colliderect(obstacle.rect):
                self.game_over = True

    def update_score(self):
        for obstacle in self.obstacles:
            if not obstacle.passed and obstacle.rect.right < self.player.rect.left:
                obstacle.passed = True
                self.score += 1

    def reset(self):
        self.__init__()

def draw_text(text, size, color, x, y):
    font = pygame.font.Font(None, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    window.blit(text_surface, text_rect)

def main():
    clock = pygame.time.Clock()
    game = Game()
    running = True

    while running:
        window.fill(BLACK)

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if game.game_over:
                        game.reset()
                    else:
                        game.player.jump()

        if not game.game_over:
            # Game logic
            game.spawn_timer += 1
            game.spawn_obstacle()
            game.player.update()
            game.check_collision()
            game.update_score()

            # Update obstacles
            for obstacle in game.obstacles[:]:
                obstacle.update()
                if obstacle.rect.right < 0:
                    game.obstacles.remove(obstacle)

        # Drawing
        # Draw ground
        pygame.draw.line(window, WHITE, (0, GROUND), (WIDTH, GROUND), 3)
        
        # Draw player
        pygame.draw.rect(window, BLUE, game.player.rect)
        
        # Draw obstacles
        for obstacle in game.obstacles:
            pygame.draw.rect(window, RED, obstacle.rect)
        
        # Draw score
        draw_text(f"Score: {game.score}", 36, WHITE, WIDTH // 2, 30)
        
        # Game over screen
        if game.game_over:
            draw_text("GAME OVER! Press SPACE to restart", 48, YELLOW, WIDTH // 2, HEIGHT // 2)

        pygame.display.update()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()