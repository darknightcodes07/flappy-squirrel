import pygame
import random
import sys

# Initialize
pygame.init()
pygame.font.init()
pygame.mixer.init()

# Fullscreen Window
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WIDTH, HEIGHT = screen.get_size()
pygame.display.set_caption("Flying Squirrel")
clock = pygame.time.Clock()

# Load assets
bird_img = pygame.image.load("squirrel.png").convert_alpha()
bird_img = pygame.transform.scale(bird_img, (43,43))

bg_img = pygame.image.load("night.jpg").convert()
bg_img = pygame.transform.scale(bg_img, (WIDTH, HEIGHT))

pipe_img = pygame.image.load("pipe.png").convert_alpha()  # Your custom pipe image

# Load Background Music
pygame.mixer.music.load("bgm.mp3")
pygame.mixer.music.set_volume(0.4)

# Fonts
font = pygame.font.SysFont("Arial", 36)
small_font = pygame.font.SysFont("Arial", 24)

# Bird
class Bird:
    def __init__(self):
        self.x = 64
        self.y = HEIGHT // 2
        self.velocity = 0
        self.gravity = 0.5
        self.lift = -9
        self.image = bird_img
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        self.velocity += self.gravity
        self.velocity = min(self.velocity, 10)
        self.y += self.velocity
        if self.y > HEIGHT - 20:
            self.y = HEIGHT - 20
            self.velocity = 0
        if self.y < 20:
            self.y = 20
            self.velocity = 0

    def up(self):
        self.velocity = self.lift

    def draw(self):
        screen.blit(self.image, (self.x, self.y))

    def get_mask(self):
        return pygame.mask.from_surface(self.image)

# Pipe
class Pipe:
    def __init__(self, speed, x):
        self.gap = 170
        self.top = random.randint(50, HEIGHT - self.gap - 50)
        self.bottom = HEIGHT - self.top - self.gap
        self.x = x
        self.speed = speed
        self.passed = False

        self.pipe_img = pipe_img
        self.pipe_width = self.pipe_img.get_width()
        self.pipe_height = self.pipe_img.get_height()
        self.top_img = pygame.transform.flip(self.pipe_img, False, True)

    def update(self):
        self.x -= self.speed

    def draw(self):
        # Draw top pipe
        y = self.top - self.pipe_height
        while y > -self.pipe_height:
            screen.blit(self.top_img, (self.x, y))
            y -= self.pipe_height

        # Draw bottom pipe
        y = HEIGHT - self.bottom
        while y < HEIGHT:
            screen.blit(self.pipe_img, (self.x, y))
            y += self.pipe_height

    def offscreen(self):
        return self.x + self.pipe_width < 0

    def hits(self, bird):
        bird_mask = bird.get_mask()

        # Top pipe collision surface
        top_surface = pygame.Surface((self.pipe_width, self.top), pygame.SRCALPHA)
        y = self.top - self.pipe_height
        while y > -self.pipe_height:
            top_surface.blit(self.top_img, (0, y - (self.top - self.pipe_height)))
            y -= self.pipe_height
        top_mask = pygame.mask.from_surface(top_surface)

        # Bottom pipe collision surface
        bottom_surface = pygame.Surface((self.pipe_width, self.bottom), pygame.SRCALPHA)
        y = 0
        while y < self.bottom:
            bottom_surface.blit(self.pipe_img, (0, y))
            y += self.pipe_height
        bottom_mask = pygame.mask.from_surface(bottom_surface)

        top_offset = (int(self.x - bird.x), int(0 - bird.y))
        bottom_offset = (int(self.x - bird.x), int((HEIGHT - self.bottom) - bird.y))

        return bird_mask.overlap(top_mask, top_offset) or bird_mask.overlap(bottom_mask, bottom_offset)

# Button
class Button:
    def __init__(self, text, x, y, width, height, callback):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.callback = callback

    def draw(self):
        pygame.draw.rect(screen, (70, 70, 70), self.rect, border_radius=10)
        pygame.draw.rect(screen, (255, 255, 255), self.rect, 2, border_radius=10)
        text_surf = small_font.render(self.text, True, (255, 255, 255))
        screen.blit(text_surf, (self.rect.x + self.rect.width // 2 - text_surf.get_width() // 2,
                                self.rect.y + self.rect.height // 2 - text_surf.get_height() // 2))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            self.callback()

# Game Over Screen
def game_over_screen(score, highscore, restart_button, quit_button):
    box_rect = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 - 120, 300, 200)
    pygame.draw.rect(screen, (0, 0, 0), box_rect, border_radius=15)
    pygame.draw.rect(screen, (255, 255, 255), box_rect, 3, border_radius=15)
    screen.blit(font.render("GAME OVER", True, (255, 0, 0)), (WIDTH//2 - 100, box_rect.y + 20))
    screen.blit(small_font.render(f"Score: {score}", True, (255, 255, 255)), (WIDTH//2 - 60, box_rect.y + 70))
    screen.blit(small_font.render(f"High Score: {highscore}", True, (255, 255, 0)), (WIDTH//2 - 80, box_rect.y + 100))
    restart_button.draw()
    quit_button.draw()

def quit_game():
    pygame.quit()
    sys.exit()

def main_game(highscore):
    pygame.mixer.music.play(-1)

    bird = Bird()
    pipes = []
    frame_count = 0
    score = 0
    pipe_speed = 3
    running = True
    game_over = False

    restart_button = Button("Restart", WIDTH//2 - 110, HEIGHT//2 + 60, 100, 40,
                            lambda: pygame.event.post(pygame.event.Event(pygame.USEREVENT)))
    quit_button = Button("Quit", WIDTH//2 + 10, HEIGHT//2 + 60, 100, 40, quit_game)

    last_pipe_x = WIDTH
    pipe_gap = 220

    while running:
        screen.blit(bg_img, (0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT: quit_game()
            if event.type == pygame.KEYDOWN and not game_over and (event.key == pygame.K_SPACE or event.key == pygame.K_UP):
                bird.up()
            if event.type == pygame.USEREVENT and game_over:
                return highscore
            if game_over:
                restart_button.handle_event(event)
                quit_button.handle_event(event)

        if not game_over:
            bird.update()
            bird.draw()

            if frame_count % 75 == 0:
                new_pipe_x = last_pipe_x + pipe_gap
                pipes.append(Pipe(pipe_speed, new_pipe_x))
                last_pipe_x = new_pipe_x

            for pipe in pipes[:]:
                pipe.update()
                pipe.draw()
                if pipe.hits(bird):
                    pygame.mixer.music.stop()
                    game_over = True
                    if score > highscore:
                        highscore = score
                if not pipe.passed and pipe.x + pipe.pipe_width < bird.x:
                    pipe.passed = True
                    score += 1
                    pipe_speed += 0.065
                if pipe.offscreen():
                    pipes.remove(pipe)

            screen.blit(small_font.render(f"Score: {score}", True, (255, 255, 255)), (10, 10))
            screen.blit(small_font.render(f"High: {highscore}", True, (255, 255, 0)), (10, 35))
            frame_count += 1
        else:
            game_over_screen(score, highscore, restart_button, quit_button)

        pygame.display.flip()
        clock.tick(60)

def start_game():
    highscore = 0
    while True:
        highscore = main_game(highscore)

start_game()
