
# game.py — Core Snake game logic (rendering + state)
# Handles: snake movement, food/poison/power-ups, obstacles, HUD, level progression.

import pygame
import random
import math
from config import *


# ---------------------------------------------------------------------------
# Utility
# ---------------------------------------------------------------------------

def grid_rect(col: int, row: int) -> pygame.Rect:
    """Return the pixel Rect for a grid cell (col, row)."""
    x = col * CELL_SIZE
    y = HUD_HEIGHT + row * CELL_SIZE
    return pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)


def random_cell(exclude: set[tuple]) -> tuple[int, int]:
    """Pick a random (col, row) not in *exclude*."""
    while True:
        col = random.randint(0, GRID_COLS - 1)
        row = random.randint(0, GRID_ROWS - 1)
        if (col, row) not in exclude:
            return col, row


# ---------------------------------------------------------------------------
# Food item
# ---------------------------------------------------------------------------

class Food:
    NORMAL   = "normal"
    WEIGHTED = "weighted"
    POISON   = "poison"

    def __init__(self, col: int, row: int, kind: str = NORMAL):
        self.col   = col
        self.row   = row
        self.kind  = kind
        self.born  = pygame.time.get_ticks()

    @property
    def color(self):
        return {
            self.NORMAL:   FOOD_COLOR,
            self.WEIGHTED: WEIGHTED_FOOD_COLOR,
            self.POISON:   POISON_COLOR,
        }[self.kind]

    @property
    def points(self):
        return {self.NORMAL: 10, self.WEIGHTED: 25, self.POISON: 0}[self.kind]

    def expired(self) -> bool:
        if self.kind == self.POISON:
            return False          # poison never expires on its own
        return pygame.time.get_ticks() - self.born > FOOD_DISAPPEAR_MS

    def draw(self, surface: pygame.Surface):
        rect = grid_rect(self.col, self.row)
        inner = rect.inflate(-4, -4)
        pygame.draw.rect(surface, self.color, inner, border_radius=4)
        if self.kind == self.WEIGHTED:
            # small sparkle
            cx, cy = inner.center
            pygame.draw.circle(surface, WHITE, (cx, cy), 3)
        elif self.kind == self.POISON:
            # skull-ish X
            pygame.draw.line(surface, WHITE, inner.topleft, inner.bottomright, 2)
            pygame.draw.line(surface, WHITE, inner.topright, inner.bottomleft, 2)


# ---------------------------------------------------------------------------
# Power-up item
# ---------------------------------------------------------------------------

class PowerUp:
    SPEED  = "speed_boost"
    SLOW   = "slow_motion"
    SHIELD = "shield"

    TYPES = [SPEED, SLOW, SHIELD]
    LABELS = {SPEED: "⚡ Speed", SLOW: "🧊 Slow", SHIELD: "🛡 Shield"}

    def __init__(self, col: int, row: int, kind: str):
        self.col   = col
        self.row   = row
        self.kind  = kind
        self.born  = pygame.time.get_ticks()

    @property
    def color(self):
        return POWERUP_COLORS[self.kind]

    def expired(self) -> bool:
        return pygame.time.get_ticks() - self.born > POWERUP_SPAWN_TIMEOUT

    def draw(self, surface: pygame.Surface, tick: int):
        rect = grid_rect(self.col, self.row)
        inner = rect.inflate(-2, -2)
        # pulsing border
        pulse = abs(math.sin(tick / 300.0))
        alpha_color = tuple(int(c * (0.6 + 0.4 * pulse)) for c in self.color)
        pygame.draw.rect(surface, alpha_color, inner, border_radius=5)
        pygame.draw.rect(surface, WHITE, inner, 1, border_radius=5)
        # letter indicator
        font = pygame.font.SysFont("consolas", 11, bold=True)
        letter = self.kind[0].upper()
        txt = font.render(letter, True, WHITE)
        surface.blit(txt, txt.get_rect(center=inner.center))


# ---------------------------------------------------------------------------
# Obstacle
# ---------------------------------------------------------------------------

class Obstacle:
    def __init__(self, col: int, row: int):
        self.col = col
        self.row = row

    def draw(self, surface: pygame.Surface):
        rect = grid_rect(self.col, self.row)
        pygame.draw.rect(surface, OBSTACLE_COLOR, rect)
        pygame.draw.rect(surface, OBSTACLE_BORDER, rect, 2)


# ---------------------------------------------------------------------------
# Main game scene
# ---------------------------------------------------------------------------

class GameScene:
    """
    Encapsulates one full game run.
    Call .update() and .draw() each frame; check .game_over_flag when done.
    """

    # Directions
    UP    = ( 0, -1)
    DOWN  = ( 0,  1)
    LEFT  = (-1,  0)
    RIGHT = ( 1,  0)

    OPPOSITE = {UP: DOWN, DOWN: UP, LEFT: RIGHT, RIGHT: LEFT}

    def __init__(self, settings: dict, personal_best: int = 0):
        self.settings      = settings
        self.personal_best = personal_best
        self.snake_color   = tuple(settings.get("snake_color", list(GREEN)))

        self._reset()

    # ------------------------------------------------------------------
    # Initialisation helpers
    # ------------------------------------------------------------------

    def _reset(self):
        self.score         = 0
        self.level         = 1
        self.food_count    = 0          # foods eaten this level
        self.food_target   = 5          # foods needed to level-up
        self.game_over_flag= False
        self.paused        = False

        # Snake
        start_col = GRID_COLS // 2
        start_row = GRID_ROWS // 2
        self.snake = [(start_col, start_row),
                      (start_col - 1, start_row),
                      (start_col - 2, start_row)]
        self.direction      = self.RIGHT
        self.next_direction = self.RIGHT

        # Food / power-ups / obstacles
        self.foods: list[Food]     = []
        self.powerup: PowerUp | None = None
        self.obstacles: list[Obstacle] = []
        self._place_obstacles()
        self._spawn_food()

        # Active power-up effect
        self.active_effect:  str | None = None
        self.effect_end_ms:  int        = 0
        self.shield_active:  bool       = False

        # Speed
        self._base_fps = BASE_FPS
        self.fps       = self._current_fps()

        # Tick counter for animations
        self._tick = 0

        # Power-up spawn timer
        self._next_powerup_ms = pygame.time.get_ticks() + random.randint(5000, 15000)

    # ------------------------------------------------------------------
    # Occupied cells
    # ------------------------------------------------------------------

    def _occupied(self) -> set[tuple]:
        cells = set(self.snake)
        cells.update((f.col, f.row) for f in self.foods)
        if self.powerup:
            cells.add((self.powerup.col, self.powerup.row))
        cells.update((o.col, o.row) for o in self.obstacles)
        return cells

    # ------------------------------------------------------------------
    # Spawning
    # ------------------------------------------------------------------

    def _spawn_food(self):
        """Spawn one food item (normal/weighted/poison)."""
        occ = self._occupied()
        col, row = random_cell(occ)
        r = random.random()
        if r < POISON_CHANCE:
            kind = Food.POISON
        elif r < POISON_CHANCE + WEIGHTED_FOOD_CHANCE:
            kind = Food.WEIGHTED
        else:
            kind = Food.NORMAL
        self.foods.append(Food(col, row, kind))

    def _maybe_spawn_powerup(self):
        if self.powerup is not None:
            return
        now = pygame.time.get_ticks()
        if now >= self._next_powerup_ms:
            occ = self._occupied()
            col, row = random_cell(occ)
            kind = random.choice(PowerUp.TYPES)
            self.powerup = PowerUp(col, row, kind)
            self._next_powerup_ms = now + random.randint(10000, 20000)

    def _place_obstacles(self):
        if self.level < OBSTACLE_START_LEVEL:
            return
        count  = (self.level - OBSTACLE_START_LEVEL + 1) * OBSTACLES_PER_LEVEL
        # safe zone around snake head
        head   = self.snake[0]
        safe   = {(head[0] + dx, head[1] + dy)
                  for dx in range(-3, 4) for dy in range(-3, 4)}
        occ    = self._occupied() | safe
        placed = 0
        attempts = 0
        while placed < count and attempts < 1000:
            attempts += 1
            col = random.randint(0, GRID_COLS - 1)
            row = random.randint(0, GRID_ROWS - 1)
            if (col, row) not in occ:
                self.obstacles.append(Obstacle(col, row))
                occ.add((col, row))
                placed += 1

    # ------------------------------------------------------------------
    # Speed
    # ------------------------------------------------------------------

    def _current_fps(self) -> float:
        base = min(BASE_FPS + (self.level - 1) * FPS_INCREMENT, MAX_FPS)
        if self.active_effect == PowerUp.SPEED:
            return base * SPEED_BOOST_MULT
        if self.active_effect == PowerUp.SLOW:
            return base * SLOW_MOTION_MULT
        return float(base)

    # ------------------------------------------------------------------
    # Input
    # ------------------------------------------------------------------

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN:
            mapping = {
                pygame.K_UP:    self.UP,
                pygame.K_w:     self.UP,
                pygame.K_DOWN:  self.DOWN,
                pygame.K_s:     self.DOWN,
                pygame.K_LEFT:  self.LEFT,
                pygame.K_a:     self.LEFT,
                pygame.K_RIGHT: self.RIGHT,
                pygame.K_d:     self.RIGHT,
            }
            new_dir = mapping.get(event.key)
            if new_dir and new_dir != self.OPPOSITE.get(self.direction):
                self.next_direction = new_dir
            if event.key == pygame.K_p:
                self.paused = not self.paused

    # ------------------------------------------------------------------
    # Update (called once per game tick, not every frame)
    # ------------------------------------------------------------------

    def step(self):
        """Advance the snake by one cell. Called by the clock logic in main."""
        if self.game_over_flag or self.paused:
            return

        self.direction = self.next_direction
        head_col, head_row = self.snake[0]
        dc, dr = self.direction
        new_col = head_col + dc
        new_row = head_row + dr

        # --- Collision detection ---
        wall_hit = (new_col < 0 or new_col >= GRID_COLS or
                    new_row < 0 or new_row >= GRID_ROWS)
        self_hit  = (new_col, new_row) in self.snake[1:]
        obs_hit   = any(o.col == new_col and o.row == new_row
                        for o in self.obstacles)

        if wall_hit or self_hit or obs_hit:
            if self.shield_active:
                self.shield_active = False
                # bounce the snake back (don't move)
                return
            self.game_over_flag = True
            return

        self.snake.insert(0, (new_col, new_row))

        # --- Check food ---
        ate_food = False
        for food in self.foods[:]:
            if food.col == new_col and food.row == new_row:
                self.foods.remove(food)
                if food.kind == Food.POISON:
                    self._eat_poison()
                else:
                    self.score += food.points
                    self.food_count += 1
                ate_food = True
                break

        if not ate_food:
            self.snake.pop()   # normal move — remove tail

        # Ensure at least one food on field
        if not any(f for f in self.foods if f.kind != Food.POISON):
            self._spawn_food()

        # --- Check power-up ---
        if self.powerup and self.powerup.col == new_col and self.powerup.row == new_row:
            self._collect_powerup(self.powerup)
            self.powerup = None

        # --- Level up ---
        if self.food_count >= self.food_target:
            self._level_up()

        # --- Expire items ---
        self.foods = [f for f in self.foods if not f.expired()]
        if not self.foods:
            self._spawn_food()
        if self.powerup and self.powerup.expired():
            self.powerup = None

        # --- Check power-up effect expiry ---
        now = pygame.time.get_ticks()
        if self.active_effect and now >= self.effect_end_ms:
            self.active_effect = None
            self.fps = self._current_fps()

        self._maybe_spawn_powerup()

    def _eat_poison(self):
        """Shorten snake by 2; game over if length drops to ≤ 1."""
        for _ in range(2):
            if len(self.snake) > 1:
                self.snake.pop()
        if len(self.snake) <= 1:
            self.game_over_flag = True

    def _collect_powerup(self, pu: PowerUp):
        now = pygame.time.get_ticks()
        if pu.kind == PowerUp.SHIELD:
            self.shield_active = True
        else:
            self.active_effect = pu.kind
            self.effect_end_ms = now + POWERUP_DURATION
            self.fps = self._current_fps()

    def _level_up(self):
        self.level      += 1
        self.food_count  = 0
        self.food_target += 2    # each level needs more food
        self.fps         = self._current_fps()
        self._place_obstacles()

    # ------------------------------------------------------------------
    # Draw
    # ------------------------------------------------------------------

    def draw(self, surface: pygame.Surface):
        self._tick = pygame.time.get_ticks()

        # Background
        surface.fill(DARK_GRAY)

        # Grid overlay
        if self.settings.get("grid_overlay", False):
            self._draw_grid(surface)

        # Obstacles
        for obs in self.obstacles:
            obs.draw(surface)

        # Food
        for food in self.foods:
            food.draw(surface)

        # Power-up
        if self.powerup:
            self.powerup.draw(surface, self._tick)

        # Snake
        self._draw_snake(surface)

        # HUD
        self._draw_hud(surface)

    def _draw_grid(self, surface: pygame.Surface):
        for col in range(GRID_COLS):
            x = col * CELL_SIZE
            pygame.draw.line(surface, GRAY,
                             (x, HUD_HEIGHT), (x, WINDOW_HEIGHT), 1)
        for row in range(GRID_ROWS):
            y = HUD_HEIGHT + row * CELL_SIZE
            pygame.draw.line(surface, GRAY,
                             (0, y), (WINDOW_WIDTH, y), 1)

    def _draw_snake(self, surface: pygame.Surface):
        for i, (col, row) in enumerate(self.snake):
            rect  = grid_rect(col, row)
            inner = rect.inflate(-2, -2)
            # Head slightly brighter
            color = WHITE if i == 0 else self.snake_color
            pygame.draw.rect(surface, color, inner, border_radius=4)
            if self.shield_active and i == 0:
                pygame.draw.rect(surface, CYAN, inner, 2, border_radius=4)

    def _draw_hud(self, surface: pygame.Surface):
        hud_rect = pygame.Rect(0, 0, WINDOW_WIDTH, HUD_HEIGHT)
        pygame.draw.rect(surface, HUD_BG, hud_rect)
        pygame.draw.line(surface, BTN_BORDER, (0, HUD_HEIGHT), (WINDOW_WIDTH, HUD_HEIGHT), 2)

        font_m = pygame.font.SysFont("consolas", 20, bold=True)
        font_s = pygame.font.SysFont("consolas", 14)

        items = [
            (f"SCORE  {self.score:06d}", HUD_ACCENT),
            (f"LEVEL  {self.level}",      HUD_TEXT),
            (f"BEST   {self.personal_best:06d}", YELLOW),
        ]
        x = 20
        for text, color in items:
            surf = font_m.render(text, True, color)
            surface.blit(surf, (x, 15))
            x += surf.get_width() + 40

        # Length
        surf = font_s.render(f"LEN {len(self.snake)}", True, LIGHT_GRAY)
        surface.blit(surf, (WINDOW_WIDTH - 120, 10))

        # Active effect
        if self.shield_active:
            eff_txt = "🛡 SHIELD"
            eff_col = PURPLE
        elif self.active_effect:
            remaining = max(0, self.effect_end_ms - pygame.time.get_ticks())
            label = PowerUp.LABELS.get(self.active_effect, self.active_effect)
            eff_txt = f"{label} {remaining//1000+1}s"
            eff_col = POWERUP_COLORS[self.active_effect]
        else:
            eff_txt = ""
            eff_col = WHITE

        if eff_txt:
            surf = font_s.render(eff_txt, True, eff_col)
            surface.blit(surf, (WINDOW_WIDTH - 200, 35))

        if self.paused:
            p_surf = pygame.font.SysFont("consolas", 28, bold=True).render("⏸ PAUSED", True, YELLOW)
            surface.blit(p_surf, p_surf.get_rect(center=(WINDOW_WIDTH // 2, HUD_HEIGHT // 2)))

        # Food progress bar
        bar_w  = 200
        bar_h  = 8
        bar_x  = (WINDOW_WIDTH - bar_w) // 2
        bar_y  = HUD_HEIGHT - 18
        ratio  = min(self.food_count / max(self.food_target, 1), 1.0)
        pygame.draw.rect(surface, GRAY, (bar_x, bar_y, bar_w, bar_h), border_radius=4)
        pygame.draw.rect(surface, HUD_ACCENT, (bar_x, bar_y, int(bar_w * ratio), bar_h), border_radius=4)
        lbl = font_s.render(f"{self.food_count}/{self.food_target}", True, LIGHT_GRAY)
        surface.blit(lbl, (bar_x + bar_w + 8, bar_y - 3))