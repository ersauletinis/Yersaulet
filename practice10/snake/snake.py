"""
Snake Game - Extended version (based on Wormy / Nibbles)
Extended from lecture example (Wormy by Al Sweigart)

Added features:
  1. Border (wall) collision check → game over when snake exits grid
  2. Food spawns only on empty cells (not on snake or walls)
  3. Levels: every 3 foods eaten advances to next level
  4. Speed increases with each level
  5. HUD shows score, level, and speed
  6. All code is commented
"""

import random
import pygame
import sys
from pygame.locals import *

# ── Window & grid settings ─────────────────────────────────────────────────────
FPS_BASE      = 8          # frames per second at level 1
WINDOW_WIDTH  = 640
WINDOW_HEIGHT = 480
CELL_SIZE     = 20
assert WINDOW_WIDTH  % CELL_SIZE == 0
assert WINDOW_HEIGHT % CELL_SIZE == 0
CELL_W = WINDOW_WIDTH  // CELL_SIZE   # grid columns
CELL_H = WINDOW_HEIGHT // CELL_SIZE   # grid rows

FOOD_PER_LEVEL = 3   # foods to eat before leveling up
SPEED_INCREASE = 2   # extra FPS added per level

# ── Colors ─────────────────────────────────────────────────────────────────────
WHITE     = (255, 255, 255)
BLACK     = (  0,   0,   0)
GREEN     = (  0, 255,   0)
DARKGREEN = (  0, 155,   0)
RED       = (255,   0,   0)
DARKGRAY  = ( 40,  40,  40)
YELLOW    = (255, 220,   0)
BGCOLOR   = BLACK

# ── Directions ─────────────────────────────────────────────────────────────────
UP    = 'up'
DOWN  = 'down'
LEFT  = 'left'
RIGHT = 'right'

HEAD = 0   # index 0 of snake list is always the head


def main():
    """Entry point: initialise pygame, show start screen, then loop game."""
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
    """Main gameplay loop."""
    # ── Starting state ─────────────────────────────────────────────────────────
    startx = random.randint(5, CELL_W - 6)
    starty = random.randint(5, CELL_H - 6)
    # Snake starts with 3 segments moving right
    snake = [
        {'x': startx,     'y': starty},
        {'x': startx - 1, 'y': starty},
        {'x': startx - 2, 'y': starty},
    ]
    direction      = RIGHT
    next_direction = RIGHT  # buffered direction from keyboard

    score          = 0      # number of foods eaten
    level          = 1      # current level
    foods_this_lvl = 0      # foods eaten on current level

    food = get_random_food(snake)   # spawn first food
    current_fps = FPS_BASE          # starts slow, increases with level

    while True:
        # ── Event handling ─────────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            elif event.type == KEYDOWN:
                # Direction keys (prevent reversing)
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

        direction = next_direction   # apply buffered direction

        # ── 1. Border (wall) collision check ───────────────────────────────────
        # If the head moves outside the grid → game over
        head = snake[HEAD]
        if head['x'] < 0 or head['x'] >= CELL_W or \
           head['y'] < 0 or head['y'] >= CELL_H:
            return   # exit run_game → triggers game-over screen

        # ── 2. Self-collision check ────────────────────────────────────────────
        for segment in snake[1:]:
            if segment['x'] == head['x'] and segment['y'] == head['y']:
                return   # hit own body → game over

        # ── 3. Check if snake ate the food ────────────────────────────────────
        if head['x'] == food['x'] and head['y'] == food['y']:
            score          += 1
            foods_this_lvl += 1
            # Don't remove tail → snake grows by 1
            food = get_random_food(snake)   # spawn new food on empty cell

            # ── 4. Level up every FOOD_PER_LEVEL foods ────────────────────────
            if foods_this_lvl >= FOOD_PER_LEVEL:
                level          += 1
                foods_this_lvl  = 0
                # 5. Increase speed with each new level
                current_fps = FPS_BASE + (level - 1) * SPEED_INCREASE
        else:
            del snake[-1]   # remove tail (snake moves without growing)

        # ── Compute new head position ──────────────────────────────────────────
        if   direction == UP:
            new_head = {'x': head['x'],     'y': head['y'] - 1}
        elif direction == DOWN:
            new_head = {'x': head['x'],     'y': head['y'] + 1}
        elif direction == LEFT:
            new_head = {'x': head['x'] - 1, 'y': head['y']}
        elif direction == RIGHT:
            new_head = {'x': head['x'] + 1, 'y': head['y']}

        snake.insert(0, new_head)   # prepend new head

        # ── Drawing ───────────────────────────────────────────────────────────
        DISPLAYSURF.fill(BGCOLOR)
        draw_grid()
        draw_snake(snake)
        draw_food(food)
        # 5. Draw HUD (score, level, speed)
        draw_hud(score, level, current_fps, foods_this_lvl)

        pygame.display.update()
        FPSCLOCK.tick(current_fps)   # speed controlled by level


def get_random_food(snake):
    """
    Generate food position that does NOT overlap the snake body.
    Keeps retrying until an empty cell is found.
    """
    snake_cells = set((s['x'], s['y']) for s in snake)
    while True:
        x = random.randint(0, CELL_W - 1)
        y = random.randint(0, CELL_H - 1)
        if (x, y) not in snake_cells:
            return {'x': x, 'y': y}


def draw_hud(score, level, fps, foods_this_lvl):
    """Render score, level progress, and speed on screen."""
    # Score (top-right)
    score_surf = BASICFONT.render(f'Score: {score}', True, WHITE)
    DISPLAYSURF.blit(score_surf, (WINDOW_WIDTH - 130, 10))

    # Level (top-left)
    level_surf = BASICFONT.render(f'Level: {level}', True, YELLOW)
    DISPLAYSURF.blit(level_surf, (10, 10))

    # Progress to next level (below level)
    prog_surf = BASICFONT.render(
        f'Next lvl: {foods_this_lvl}/{FOOD_PER_LEVEL}', True, DARKGRAY
    )
    DISPLAYSURF.blit(prog_surf, (10, 34))

    # Speed (top-center)
    spd_surf = BASICFONT.render(f'Speed: {fps}', True, (150, 200, 255))
    DISPLAYSURF.blit(spd_surf, (WINDOW_WIDTH // 2 - spd_surf.get_width() // 2, 10))


def draw_snake(snake):
    """Draw each segment of the snake as a two-tone green square."""
    for coord in snake:
        x = coord['x'] * CELL_SIZE
        y = coord['y'] * CELL_SIZE
        # Outer dark-green border
        pygame.draw.rect(DISPLAYSURF, DARKGREEN,
                         pygame.Rect(x, y, CELL_SIZE, CELL_SIZE))
        # Inner bright-green fill (gives a 3-D look)
        pygame.draw.rect(DISPLAYSURF, GREEN,
                         pygame.Rect(x + 4, y + 4, CELL_SIZE - 8, CELL_SIZE - 8))


def draw_food(coord):
    """Draw the food as a red square."""
    x = coord['x'] * CELL_SIZE
    y = coord['y'] * CELL_SIZE
    pygame.draw.rect(DISPLAYSURF, RED, pygame.Rect(x, y, CELL_SIZE, CELL_SIZE))


def draw_grid():
    """Draw subtle dark-gray grid lines over the black background."""
    for x in range(0, WINDOW_WIDTH,  CELL_SIZE):
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (x, 0), (x, WINDOW_HEIGHT))
    for y in range(0, WINDOW_HEIGHT, CELL_SIZE):
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (0, y), (WINDOW_WIDTH, y))


def show_start_screen():
    """Spinning title screen; any key starts the game."""
    title_font = pygame.font.Font('freesansbold.ttf', 80)
    surf1 = title_font.render('SNAKE', True, WHITE, DARKGREEN)
    surf2 = title_font.render('SNAKE', True, GREEN)
    deg1 = deg2 = 0

    while True:
        DISPLAYSURF.fill(BGCOLOR)
        # Two layers of rotating text
        for surf, deg, step in [(surf1, deg1, 3), (surf2, deg2, 7)]:
            rot  = pygame.transform.rotate(surf, deg)
            rect = rot.get_rect()
            rect.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
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
    """Show GAME OVER in large text; any key restarts."""
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
    check_for_key()   # flush queue

    while True:
        if check_for_key():
            pygame.event.get()
            return


def draw_press_key():
    """Render 'Press a key' hint in the bottom-right corner."""
    surf = BASICFONT.render('Press a key to play.', True, DARKGRAY)
    rect = surf.get_rect(bottomright=(WINDOW_WIDTH - 10, WINDOW_HEIGHT - 10))
    DISPLAYSURF.blit(surf, rect)


def check_for_key():
    """Return the key pressed (or None). Quit on Escape / window-close."""
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
