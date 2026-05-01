# Imports
import pygame, sys, random, time
from pygame.locals import *

# Initializing pygame and sound mixer
pygame.init()
pygame.mixer.init()

# FPS limiter
FPS = 60
FramePerSec = pygame.time.Clock()

# Colors
RED    = (255,   0,   0)
BLACK  = (  0,   0,   0)
WHITE  = (255, 255, 255)
YELLOW = (255, 220,   0)
GOLD   = (255, 180,   0)
CYAN   = (  0, 220, 255)

# Screen / game settings
SCREEN_WIDTH  = 400
SCREEN_HEIGHT = 600
SPEED         = 5          # current game speed (increases over time)
SCORE         = 0          # enemies dodged
COINS         = 0          # total coin value collected

# Threshold: every N coin-points earned, enemy gets a speed boost
COIN_SPEED_THRESHOLD = 10  # boost fires at 10, 20, 30 … coin points
_last_boost_at       = 0   # tracks last threshold crossed
ENEMY_SPEED_BOOST    = 1.5 # how much SPEED rises per threshold crossing

# Spawn probability per frame for a new coin
COIN_SPAWN_CHANCE = 0.004

# Fonts
font           = pygame.font.SysFont("Verdana", 60)
font_small     = pygame.font.SysFont("Verdana", 20)
game_over_text = font.render("Game Over", True, BLACK)

# Load scrolling road background
background = pygame.image.load("racer/AnimatedStreet.png")
bg_y1 = 0
bg_y2 = -SCREEN_HEIGHT   # second copy starts one screen above

# Display surface
DISPLAYSURF = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
DISPLAYSURF.fill(WHITE)
pygame.display.set_caption("Racer")

# Background music (loop forever)
pygame.mixer.music.load("racer/background.wav")
pygame.mixer.music.play(-1)

# Crash sound loaded once, played on collision
crash_sound = pygame.mixer.Sound("racer/crash.wav")

# ── Coin weight table ─────────────────────────────────────────────────────────
# Each entry: (point_value, color, radius, spawn_weight)
# spawn_weight controls how likely this tier is to appear (higher = rarer)
COIN_TYPES = [
    {"value": 1,  "color": YELLOW, "radius": 10, "weight": 60},  # common bronze
    {"value": 3,  "color": GOLD,   "radius": 13, "weight": 30},  # uncommon gold
    {"value": 5,  "color": CYAN,   "radius": 16, "weight": 10},  # rare diamond
]
# Pre-compute cumulative weights for weighted random selection
_cum_weights = []
_running = 0
for ct in COIN_TYPES:
    _running += ct["weight"]
    _cum_weights.append(_running)
_total_weight = _running


def pick_coin_type() -> dict:
    """Return a random coin-type dict using weighted probability."""
    r = random.randint(1, _total_weight)
    for i, cum in enumerate(_cum_weights):
        if r <= cum:
            return COIN_TYPES[i]
    return COIN_TYPES[0]


# ── Enemy sprite ──────────────────────────────────────────────────────────────
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("racer/Enemy.png").convert_alpha()
        self.rect  = self.image.get_rect()
        # Spawn at random horizontal position, just above the screen
        self.rect.center = (random.randint(40, SCREEN_WIDTH - 40), 0)

    def move(self):
        """Move downward at current SPEED; award a dodge point when off-screen."""
        global SCORE
        self.rect.move_ip(0, SPEED)
        if self.rect.top > SCREEN_HEIGHT:
            SCORE += 1
            # Reposition back to the top
            self.rect.center = (random.randint(40, SCREEN_WIDTH - 40), 0)


# ── Player sprite ─────────────────────────────────────────────────────────────
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("racer/Player.png").convert_alpha()
        self.rect  = self.image.get_rect()
        self.rect.center = (160, 520)

    def move(self):
        """Move left/right with arrow keys; clamp to screen boundaries."""
        pressed = pygame.key.get_pressed()
        if self.rect.left > 0 and pressed[K_LEFT]:
            self.rect.move_ip(-5, 0)
        if self.rect.right < SCREEN_WIDTH and pressed[K_RIGHT]:
            self.rect.move_ip(5, 0)


# ── Coin sprite ───────────────────────────────────────────────────────────────
class Coin(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # Choose a random weighted tier
        ctype = pick_coin_type()
        self.value  = ctype["value"]   # how many coin-points this coin is worth
        radius      = ctype["radius"]
        color       = ctype["color"]

        # Draw the coin as a filled circle on a transparent surface
        size = radius * 2 + 4
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(self.image, color,       (size // 2, size // 2), radius)
        pygame.draw.circle(self.image, (0, 0, 0),   (size // 2, size // 2), radius, 2)  # outline

        self.rect = self.image.get_rect()
        self.rect.center = (random.randint(40, SCREEN_WIDTH - 40), -20)

    def move(self):
        """Fall at game speed; remove if it exits the screen uncollected."""
        self.rect.move_ip(0, SPEED)
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()   # remove from all groups


# ── Sprite setup ──────────────────────────────────────────────────────────────
P1 = Player()
E1 = Enemy()

enemies     = pygame.sprite.Group()
coins_grp   = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()

enemies.add(E1)
all_sprites.add(P1, E1)

# Timer event: fires every 1 000 ms to gradually increase game speed
INC_SPEED = pygame.USEREVENT + 1
pygame.time.set_timer(INC_SPEED, 1000)


def draw_background():
    """Scroll two copies of the road image for an infinite road illusion."""
    global bg_y1, bg_y2
    scroll = SPEED * 0.5   # background scrolls slower than cars (parallax)
    bg_y1 += scroll
    bg_y2 += scroll
    # Wrap each copy when it fully exits the bottom
    if bg_y1 >= SCREEN_HEIGHT:
        bg_y1 = bg_y2 - SCREEN_HEIGHT
    if bg_y2 >= SCREEN_HEIGHT:
        bg_y2 = bg_y1 - SCREEN_HEIGHT
    DISPLAYSURF.blit(background, (0, int(bg_y1)))
    DISPLAYSURF.blit(background, (0, int(bg_y2)))


def check_coin_speed_boost():
    """
    If the player crossed a new COIN_SPEED_THRESHOLD milestone,
    immediately increase SPEED by ENEMY_SPEED_BOOST.
    """
    global COINS, SPEED, _last_boost_at
    milestone = (COINS // COIN_SPEED_THRESHOLD) * COIN_SPEED_THRESHOLD
    if milestone > _last_boost_at:
        SPEED += ENEMY_SPEED_BOOST
        _last_boost_at = milestone


# ── Main game loop ────────────────────────────────────────────────────────────
while True:
    for event in pygame.event.get():
        if event.type == INC_SPEED:
            SPEED += 0.5          # baseline speed increase every second
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    # Draw scrolling road background
    draw_background()

    # Randomly spawn a new coin each frame based on spawn chance
    if random.random() < COIN_SPAWN_CHANCE:
        coin = Coin()
        coins_grp.add(coin)
        all_sprites.add(coin)

    # Move and draw every sprite
    for entity in all_sprites:
        entity.move()
        DISPLAYSURF.blit(entity.image, entity.rect)

    # ── HUD ───────────────────────────────────────────────────────────────────
    score_surf = font_small.render(f"Score: {SCORE}", True, WHITE)
    DISPLAYSURF.blit(score_surf, (10, 10))

    coin_surf = font_small.render(f"Coins: {COINS}", True, YELLOW)
    DISPLAYSURF.blit(coin_surf, (SCREEN_WIDTH - coin_surf.get_width() - 10, 10))

    # Show next boost milestone so player knows how far away it is
    next_milestone = ((_last_boost_at // COIN_SPEED_THRESHOLD) + 1) * COIN_SPEED_THRESHOLD
    boost_surf = font_small.render(f"Boost at: {next_milestone}", True, CYAN)
    DISPLAYSURF.blit(boost_surf, (SCREEN_WIDTH - boost_surf.get_width() - 10, 34))

    # Coin legend (bottom-left): show what each colour is worth
    for i, ct in enumerate(COIN_TYPES):
        pygame.draw.circle(DISPLAYSURF, ct["color"], (18, SCREEN_HEIGHT - 56 + i * 18), 7)
        legend = font_small.render(f"= {ct['value']} pt", True, WHITE)
        DISPLAYSURF.blit(legend, (30, SCREEN_HEIGHT - 63 + i * 18))

    # ── Coin collection ───────────────────────────────────────────────────────
    collected = pygame.sprite.spritecollide(P1, coins_grp, True)
    for coin in collected:
        COINS += coin.value          # add weighted value, not just 1

    # Check whether a speed boost milestone was just crossed
    check_coin_speed_boost()

    # ── Enemy collision → Game Over ───────────────────────────────────────────
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