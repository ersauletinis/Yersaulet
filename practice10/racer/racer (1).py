# Imports
import pygame, sys, random, time
from pygame.locals import *

# Initializing
pygame.init()
pygame.mixer.init()

# FPS
FPS = 60
FramePerSec = pygame.time.Clock()

# Colors
RED    = (255,   0,   0)
BLACK  = (  0,   0,   0)
WHITE  = (255, 255, 255)
YELLOW = (255, 220,   0)

# Screen variables
SCREEN_WIDTH  = 400
SCREEN_HEIGHT = 600
SPEED = 5
SCORE = 0   # enemies dodged
COINS = 0   # coins collected

# Fonts
font           = pygame.font.SysFont("Verdana", 60)
font_small     = pygame.font.SysFont("Verdana", 20)
game_over_text = font.render("Game Over", True, BLACK)

# Load background image (road)
background = pygame.image.load("racer/AnimatedStreet.png")
# Two copies scrolled vertically for an infinite road effect
bg_y1 = 0
bg_y2 = -SCREEN_HEIGHT

# Display
DISPLAYSURF = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Racer")

# Background music (loop forever = -1)
pygame.mixer.music.load("racer/background.wav")
pygame.mixer.music.play(-1)

# Crash sound loaded once, reused on collision
crash_sound = pygame.mixer.Sound("racer/crash.wav")

# Load and scale coin image
# The coin PNG has a black background, so we remove it with set_colorkey
coin_img_raw = pygame.image.load("racer/27931687789b285f4c82b6339025c55a.png").convert()
coin_img_raw.set_colorkey((0, 0, 0))
coin_img = pygame.transform.scale(coin_img_raw, (30, 30))

# Chance per frame that a new coin spawns on the road
COIN_SPAWN_CHANCE = 0.004


# ── Enemy sprite ──────────────────────────────────────────────────────────────
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("racer/Enemy.png").convert_alpha()
        self.rect  = self.image.get_rect()
        self.rect.center = (random.randint(40, SCREEN_WIDTH - 40), 0)

    def move(self):
        """Move downward; reset to top when off-screen (counts as dodge)."""
        global SCORE
        self.rect.move_ip(0, SPEED)
        if self.rect.top > SCREEN_HEIGHT:
            SCORE += 1
            self.rect.center = (random.randint(40, SCREEN_WIDTH - 40), 0)


# ── Player sprite ─────────────────────────────────────────────────────────────
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("racer/Player.png").convert_alpha()
        self.rect  = self.image.get_rect()
        self.rect.center = (160, 520)

    def move(self):
        """Move left/right with arrow keys; clamp to screen edges."""
        pressed = pygame.key.get_pressed()
        if self.rect.left > 0 and pressed[K_LEFT]:
            self.rect.move_ip(-5, 0)
        if self.rect.right < SCREEN_WIDTH and pressed[K_RIGHT]:
            self.rect.move_ip(5, 0)


# ── Coin sprite ───────────────────────────────────────────────────────────────
class Coin(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = coin_img   # reuse pre-scaled surface
        self.rect  = self.image.get_rect()
        self.rect.center = (random.randint(40, SCREEN_WIDTH - 40), -20)

    def move(self):
        """Move downward with traffic speed; disappear if not collected."""
        self.rect.move_ip(0, SPEED)
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()   # remove from all sprite groups


# ── Sprite setup ──────────────────────────────────────────────────────────────
P1 = Player()
E1 = Enemy()

enemies     = pygame.sprite.Group()
coins_grp   = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()

enemies.add(E1)
all_sprites.add(P1, E1)

# User event: fires every 1000 ms to increase speed
INC_SPEED = pygame.USEREVENT + 1
pygame.time.set_timer(INC_SPEED, 1000)


def draw_background():
    """Scroll two copies of road image downward (infinite road illusion)."""
    global bg_y1, bg_y2
    scroll = SPEED * 0.5   # background scrolls slower than cars (depth effect)
    bg_y1 += scroll
    bg_y2 += scroll
    if bg_y1 >= SCREEN_HEIGHT:
        bg_y1 = bg_y2 - SCREEN_HEIGHT
    if bg_y2 >= SCREEN_HEIGHT:
        bg_y2 = bg_y1 - SCREEN_HEIGHT
    DISPLAYSURF.blit(background, (0, int(bg_y1)))
    DISPLAYSURF.blit(background, (0, int(bg_y2)))


# ── Main game loop ────────────────────────────────────────────────────────────
while True:
    for event in pygame.event.get():
        if event.type == INC_SPEED:
            SPEED += 0.5          # game gets faster every second
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    # Draw scrolling road
    draw_background()

    # Randomly spawn a coin
    if random.random() < COIN_SPAWN_CHANCE:
        coin = Coin()
        coins_grp.add(coin)
        all_sprites.add(coin)

    # Move and draw all sprites
    for entity in all_sprites:
        entity.move()
        DISPLAYSURF.blit(entity.image, entity.rect)

    # HUD — score top-left, coins top-right
    score_surf = font_small.render(f"Score: {SCORE}", True, WHITE)
    DISPLAYSURF.blit(score_surf, (10, 10))

    coin_surf = font_small.render(f"Coins: {COINS}", True, YELLOW)
    DISPLAYSURF.blit(coin_surf, (SCREEN_WIDTH - coin_surf.get_width() - 10, 10))

    # Check if player collected any coins (True = remove coin on hit)
    collected = pygame.sprite.spritecollide(P1, coins_grp, True)
    COINS += len(collected)

    # Collision with enemy car → Game Over
    if pygame.sprite.spritecollideany(P1, enemies):
        pygame.mixer.music.stop()
        crash_sound.play()
        time.sleep(1)

        DISPLAYSURF.fill(RED)
        DISPLAYSURF.blit(game_over_text, (30, 220))
        final = font_small.render(f"Score: {SCORE}   Coins: {COINS}", True, WHITE)
        DISPLAYSURF.blit(final, (SCREEN_WIDTH // 2 - final.get_width() // 2, 310))
        pygame.display.update()

        for entity in all_sprites:
            entity.kill()
        time.sleep(2)
        pygame.quit()
        sys.exit()

    pygame.display.update()
    FramePerSec.tick(FPS)
