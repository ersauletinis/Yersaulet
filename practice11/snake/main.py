"""
Snake Game — Extended (Practice 8+)
=====================================
Added on top of the lecture base:
  1. Weighted food: 3 tiers with different point values and colours
  2. Food disappears after a timer (rare food disappears faster)
  3. All new code is commented
"""
 
import random
import pygame
import sys
from pygame.locals import *
 
# ── Window & grid ──────────────────────────────────────────────────────────────
FPS_BASE      = 8
WINDOW_WIDTH  = 640
WINDOW_HEIGHT = 480
CELL_SIZE     = 20
assert WINDOW_WIDTH  % CELL_SIZE == 0
assert WINDOW_HEIGHT % CELL_SIZE == 0
CELL_W = WINDOW_WIDTH  // CELL_SIZE
CELL_H = WINDOW_HEIGHT // CELL_SIZE
 
FOOD_PER_LEVEL = 3
SPEED_INCREASE = 2
 
# ── Colours ────────────────────────────────────────────────────────────────────
WHITE     = (255, 255, 255)
BLACK     = (  0,   0,   0)
GREEN     = (  0, 255,   0)
DARKGREEN = (  0, 155,   0)
DARKGRAY  = ( 40,  40,  40)
YELLOW    = (255, 220,   0)
BGCOLOR   = BLACK
 
# ── Directions ─────────────────────────────────────────────────────────────────
UP    = 'up'
DOWN  = 'down'
LEFT  = 'left'
RIGHT = 'right'
HEAD  = 0
 
# ── Weighted food types ────────────────────────────────────────────────────────
# Each tier defines:
#   value       — score points when eaten
#   color       — drawn colour on grid
#   lifetime_ms — milliseconds before the food disappears (None = never)
#   weight      — relative spawn probability (higher = more common)
FOOD_TYPES = [
    {
        'value':       1,
        'color':       (220,  60,  60),   # red   — common apple
        'lifetime_ms': 6000,              # 6 seconds
        'weight':      60,
    },
    {
        'value':       3,
        'color':       (255, 165,   0),   # orange — uncommon
        'lifetime_ms': 4000,              # 4 seconds (disappears faster)
        'weight':      30,
    },
    {
        'value':       5,
        'color':       (80,  200, 255),   # cyan  — rare gem
        'lifetime_ms': 2500,              # 2.5 seconds (very fast)
        'weight':      10,
    },
]
 
# Pre-compute cumulative weights for O(n) weighted random pick
_CUM_WEIGHTS = []
_running = 0
for _ft in FOOD_TYPES:
    _running += _ft['weight']
    _CUM_WEIGHTS.append(_running)
_TOTAL_WEIGHT = _running
 
 
def pick_food_type() -> dict:
    """Return a random food-type dict using weighted probability."""
    r = random.randint(1, _TOTAL_WEIGHT)
    for i, cum in enumerate(_CUM_WEIGHTS):
        if r <= cum:
            return FOOD_TYPES[i]
    return FOOD_TYPES[0]
 
 
def get_random_food(snake: list) -> dict:
    """
    Spawn a new food item on an empty cell.
    Chooses a weighted random tier and records the spawn time
    so we can expire it after lifetime_ms milliseconds.
    """
    snake_cells = {(s['x'], s['y']) for s in snake}
    while True:
        x = random.randint(0, CELL_W - 1)
        y = random.randint(0, CELL_H - 1)
        if (x, y) not in snake_cells:
            ftype = pick_food_type()
            return {
                'x':           x,
                'y':           y,
                'value':       ftype['value'],
                'color':       ftype['color'],
                'lifetime_ms': ftype['lifetime_ms'],
                'spawned_at':  pygame.time.get_ticks(),  # timestamp for timer
            }
 
 
def food_expired(food: dict) -> bool:
    """Return True if the food has been on the grid longer than its lifetime."""
    elapsed = pygame.time.get_ticks() - food['spawned_at']
    return elapsed >= food['lifetime_ms']
 
 
def food_alpha(food: dict) -> int:
    """
    Return 0-255 opacity for the food based on remaining time.
    Food starts fully opaque and fades to ~80 in the last 800 ms.
    """
    elapsed   = pygame.time.get_ticks() - food['spawned_at']
    remaining = food['lifetime_ms'] - elapsed
    if remaining > 800:
        return 255
    # Fade from 255 → 80 over the last 800 ms
    return max(80, int(255 * remaining / 800))
 
 
# ── Main ───────────────────────────────────────────────────────────────────────
 
def main():
    global FPSCLOCK, DISPLAYSURF, BASICFONT
    pygame.init()
    FPSCLOCK    = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    BASICFONT   = pygame.font.Font('freesansbold.ttf', 18)
    pygame.display.set_caption('Snake — Extended')
 
    show_start_screen()
    while True:
        run_game()
        show_game_over_screen()
 
 
def run_game():
    """Main gameplay loop with weighted, expiring food."""
    startx = random.randint(5, CELL_W - 6)
    starty = random.randint(5, CELL_H - 6)
    snake  = [
        {'x': startx,     'y': starty},
        {'x': startx - 1, 'y': starty},
        {'x': startx - 2, 'y': starty},
    ]
    direction      = RIGHT
    next_direction = RIGHT
 
    score          = 0
    level          = 1
    foods_this_lvl = 0
    current_fps    = FPS_BASE
 
    # Active food items on the grid (can keep multiple if desired)
    foods = [get_random_food(snake)]
 
    while True:
        # ── Events ────────────────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            elif event.type == KEYDOWN:
                if   event.key in (K_LEFT,  K_a) and direction != RIGHT:
                    next_direction = LEFT
                elif event.key in (K_RIGHT, K_d) and direction != LEFT:
                    next_direction = RIGHT
                elif event.key in (K_UP,    K_w) and direction != DOWN:
                    next_direction = UP
                elif event.key in (K_DOWN,  K_s) and direction != UP:
                    next_direction = DOWN
                elif event.key == K_ESCAPE:
                    terminate()
 
        direction = next_direction
 
        # ── Border collision ───────────────────────────────────────────────────
        head = snake[HEAD]
        if head['x'] < 0 or head['x'] >= CELL_W or \
           head['y'] < 0 or head['y'] >= CELL_H:
            return
 
        # ── Self collision ─────────────────────────────────────────────────────
        for seg in snake[1:]:
            if seg['x'] == head['x'] and seg['y'] == head['y']:
                return
 
        # ── Food expiry: remove timed-out food, spawn replacement ──────────────
        expired = [f for f in foods if food_expired(f)]
        for f in expired:
            foods.remove(f)
            foods.append(get_random_food(snake))  # replace each expired item
 
        # ── Food collection ────────────────────────────────────────────────────
        eaten = None
        for f in foods:
            if head['x'] == f['x'] and head['y'] == f['y']:
                eaten = f
                break
 
        if eaten:
            score          += eaten['value']   # add weighted value
            foods_this_lvl += 1
            foods.remove(eaten)
            foods.append(get_random_food(snake))   # spawn replacement
 
            # Level up
            if foods_this_lvl >= FOOD_PER_LEVEL:
                level          += 1
                foods_this_lvl  = 0
                current_fps     = FPS_BASE + (level - 1) * SPEED_INCREASE
            # Snake grows: DON'T remove tail this tick
        else:
            del snake[-1]   # normal move: remove tail
 
        # ── New head ───────────────────────────────────────────────────────────
        if   direction == UP:
            new_head = {'x': head['x'],     'y': head['y'] - 1}
        elif direction == DOWN:
            new_head = {'x': head['x'],     'y': head['y'] + 1}
        elif direction == LEFT:
            new_head = {'x': head['x'] - 1, 'y': head['y']}
        elif direction == RIGHT:
            new_head = {'x': head['x'] + 1, 'y': head['y']}
        snake.insert(0, new_head)
 
        # ── Draw ───────────────────────────────────────────────────────────────
        DISPLAYSURF.fill(BGCOLOR)
        draw_grid()
        draw_snake(snake)
        for f in foods:
            draw_food(f)               # each food drawn with fade effect
        draw_hud(score, level, current_fps, foods_this_lvl)
        draw_food_legend()             # colour legend bottom-right
 
        pygame.display.update()
        FPSCLOCK.tick(current_fps)
 
 
# ── Drawing helpers ────────────────────────────────────────────────────────────
 
def draw_food(food: dict):
    """
    Draw a food item as a filled square.
    The square fades out as the food's timer runs low.
    A small timer bar below the cell shows remaining lifetime.
    """
    x_px = food['x'] * CELL_SIZE
    y_px = food['y'] * CELL_SIZE
 
    # Fading colour based on remaining lifetime
    alpha = food_alpha(food)
    r, g, b = food['color']
    faded   = (r * alpha // 255, g * alpha // 255, b * alpha // 255)
 
    pygame.draw.rect(DISPLAYSURF, faded,
                     pygame.Rect(x_px, y_px, CELL_SIZE, CELL_SIZE))
 
    # Timer bar: thin bar below the cell showing % lifetime remaining
    elapsed   = pygame.time.get_ticks() - food['spawned_at']
    fraction  = max(0.0, 1.0 - elapsed / food['lifetime_ms'])
    bar_w     = int(CELL_SIZE * fraction)
    bar_rect  = pygame.Rect(x_px, y_px + CELL_SIZE - 3, bar_w, 3)
    pygame.draw.rect(DISPLAYSURF, WHITE, bar_rect)
 
 
def draw_food_legend():
    """Small legend in the bottom-right showing food tiers and their values."""
    font  = pygame.font.Font('freesansbold.ttf', 13)
    x_base = WINDOW_WIDTH  - 130
    y_base = WINDOW_HEIGHT - 20 - len(FOOD_TYPES) * 18
 
    for i, ft in enumerate(FOOD_TYPES):
        y = y_base + i * 18
        # Colour swatch
        pygame.draw.rect(DISPLAYSURF, ft['color'], pygame.Rect(x_base, y + 2, 12, 12))
        # Label: value and lifetime
        secs = ft['lifetime_ms'] // 1000
        lbl  = font.render(f"= {ft['value']} pt  ({secs}s)", True, DARKGRAY)
        DISPLAYSURF.blit(lbl, (x_base + 16, y))
 
 
def draw_snake(snake):
    """Draw each segment as a two-tone green square."""
    for coord in snake:
        x = coord['x'] * CELL_SIZE
        y = coord['y'] * CELL_SIZE
        pygame.draw.rect(DISPLAYSURF, DARKGREEN,
                         pygame.Rect(x, y, CELL_SIZE, CELL_SIZE))
        pygame.draw.rect(DISPLAYSURF, GREEN,
                         pygame.Rect(x + 4, y + 4, CELL_SIZE - 8, CELL_SIZE - 8))
 
 
def draw_grid():
    """Subtle dark-gray grid lines."""
    for x in range(0, WINDOW_WIDTH,  CELL_SIZE):
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (x, 0), (x, WINDOW_HEIGHT))
    for y in range(0, WINDOW_HEIGHT, CELL_SIZE):
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (0, y), (WINDOW_WIDTH, y))
 
 
def draw_hud(score, level, fps, foods_this_lvl):
    """Score, level, speed HUD."""
    score_surf = BASICFONT.render(f'Score: {score}', True, WHITE)
    DISPLAYSURF.blit(score_surf, (WINDOW_WIDTH - 130, 10))
 
    level_surf = BASICFONT.render(f'Level: {level}', True, YELLOW)
    DISPLAYSURF.blit(level_surf, (10, 10))
 
    prog_surf  = BASICFONT.render(f'Next lvl: {foods_this_lvl}/{FOOD_PER_LEVEL}',
                                  True, DARKGRAY)
    DISPLAYSURF.blit(prog_surf, (10, 34))
 
    spd_surf = BASICFONT.render(f'Speed: {fps}', True, (150, 200, 255))
    DISPLAYSURF.blit(spd_surf,
                     (WINDOW_WIDTH // 2 - spd_surf.get_width() // 2, 10))
 
 
# ── Screens ────────────────────────────────────────────────────────────────────
 
def show_start_screen():
    title_font = pygame.font.Font('freesansbold.ttf', 80)
    surf1 = title_font.render('SNAKE', True, WHITE, DARKGREEN)
    surf2 = title_font.render('SNAKE', True, GREEN)
    deg1 = deg2 = 0
    while True:
        DISPLAYSURF.fill(BGCOLOR)
        for surf, deg, step in [(surf1, deg1, 3), (surf2, deg2, 7)]:
            rot  = pygame.transform.rotate(surf, deg)
            rect = rot.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
            DISPLAYSURF.blit(rot, rect)
        draw_press_key()
        if check_for_key():
            pygame.event.get()
            return
        pygame.display.update()
        FPSCLOCK.tick(15)
        deg1 += 3
        deg2 += 7
 
 
def show_game_over_screen():
    go_font   = pygame.font.Font('freesansbold.ttf', 100)
    game_surf = go_font.render('GAME', True, WHITE)
    over_surf = go_font.render('OVER', True, WHITE)
    game_rect = game_surf.get_rect(midtop=(WINDOW_WIDTH // 2, 10))
    over_rect = over_surf.get_rect(midtop=(WINDOW_WIDTH // 2, game_rect.height + 35))
    DISPLAYSURF.blit(game_surf, game_rect)
    DISPLAYSURF.blit(over_surf, over_rect)
    draw_press_key()
    pygame.display.update()
    pygame.time.wait(500)
    check_for_key()
    while True:
        if check_for_key():
            pygame.event.get()
            return
 
 
def draw_press_key():
    surf = BASICFONT.render('Press a key to play.', True, DARKGRAY)
    rect = surf.get_rect(bottomright=(WINDOW_WIDTH - 10, WINDOW_HEIGHT - 10))
    DISPLAYSURF.blit(surf, rect)
 
 
def check_for_key():
    if pygame.event.get(QUIT):
        terminate()
    events = pygame.event.get(KEYUP)
    if not events:
        return None
    if events[0].key == K_ESCAPE:
        terminate()
    return events[0].key
 
 
def terminate():
    pygame.quit()
    sys.exit()
 
 
if __name__ == '__main__':
    main()