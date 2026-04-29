# main.py — Entry point & screen manager
# Screens: MainMenu → Game → GameOver → Leaderboard / Settings

import sys
import os
import pygame

from config import *
import settings_manager as sm
import db
from game import GameScene

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_fonts():
    pygame.font.init()
    return {
        "xl":  pygame.font.SysFont("consolas", 56, bold=True),
        "lg":  pygame.font.SysFont("consolas", 36, bold=True),
        "md":  pygame.font.SysFont("consolas", 22, bold=True),
        "sm":  pygame.font.SysFont("consolas", 16),
        "xs":  pygame.font.SysFont("consolas", 13),
    }


def draw_bg(surface: pygame.Surface, tick: int):
    """Animated dark-blue grid background."""
    surface.fill(MENU_BG)
    offset = (tick // 60) % CELL_SIZE
    for x in range(-CELL_SIZE, WINDOW_WIDTH + CELL_SIZE, CELL_SIZE):
        pygame.draw.line(surface, (20, 25, 40),
                         (x + offset, 0), (x + offset, WINDOW_HEIGHT))
    for y in range(-CELL_SIZE, WINDOW_HEIGHT + CELL_SIZE, CELL_SIZE):
        pygame.draw.line(surface, (20, 25, 40),
                         (0, y + offset), (WINDOW_WIDTH, y + offset))


class Button:
    """Simple click-able button."""

    def __init__(self, rect: pygame.Rect, label: str, fonts: dict):
        self.rect    = rect
        self.label   = label
        self.fonts   = fonts
        self.hovered = False

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(event.pos)
        return False

    def draw(self, surface: pygame.Surface):
        color  = BTN_HOVER if self.hovered else BTN_NORMAL
        border = (120, 140, 220) if self.hovered else BTN_BORDER
        pygame.draw.rect(surface, color,  self.rect, border_radius=8)
        pygame.draw.rect(surface, border, self.rect, 2, border_radius=8)
        txt = self.fonts["md"].render(self.label, True, BTN_TEXT)
        surface.blit(txt, txt.get_rect(center=self.rect.center))


# ---------------------------------------------------------------------------
# Text-input widget
# ---------------------------------------------------------------------------

class TextInput:
    def __init__(self, rect: pygame.Rect, fonts: dict, placeholder: str = ""):
        self.rect        = rect
        self.fonts       = fonts
        self.placeholder = placeholder
        self.text        = ""
        self.active      = True

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                pass   # caller checks .text
            elif len(self.text) < 20 and event.unicode.isprintable():
                self.text += event.unicode

    def draw(self, surface: pygame.Surface, tick: int):
        border_color = (100, 160, 255) if self.active else BTN_BORDER
        pygame.draw.rect(surface, BTN_NORMAL, self.rect, border_radius=6)
        pygame.draw.rect(surface, border_color, self.rect, 2, border_radius=6)
        display = self.text if self.text else self.placeholder
        color   = WHITE if self.text else GRAY
        txt     = self.fonts["md"].render(display, True, color)
        surface.blit(txt, txt.get_rect(midleft=(self.rect.x + 12, self.rect.centery)))
        # cursor blink
        if self.active and (tick // 500) % 2 == 0 and self.text:
            cx = self.rect.x + 12 + txt.get_width() + 3
            cy = self.rect.centery
            pygame.draw.line(surface, WHITE, (cx, cy - 10), (cx, cy + 10), 2)


# ---------------------------------------------------------------------------
# Screens
# ---------------------------------------------------------------------------

class ScreenBase:
    def __init__(self, app: "App"):
        self.app = app

    def handle_event(self, event: pygame.event.Event):
        pass

    def update(self):
        pass

    def draw(self, surface: pygame.Surface):
        pass


# ─── Main Menu ─────────────────────────────────────────────────────────────

class MainMenuScreen(ScreenBase):
    def __init__(self, app: "App"):
        super().__init__(app)
        f = app.fonts
        cx = WINDOW_WIDTH // 2

        self.username_label = f["md"].render("Enter username:", True, LIGHT_GRAY)

        self.input = TextInput(
            pygame.Rect(cx - 160, 220, 320, 46),
            f,
            placeholder="your name"
        )
        # pre-fill saved username
        if app.username:
            self.input.text = app.username

        btn_w, btn_h = 240, 48
        self.btn_play = Button(pygame.Rect(cx - btn_w // 2, 300, btn_w, btn_h), "▶  PLAY",        f)
        self.btn_lb   = Button(pygame.Rect(cx - btn_w // 2, 360, btn_w, btn_h), "🏆  LEADERBOARD", f)
        self.btn_cfg  = Button(pygame.Rect(cx - btn_w // 2, 420, btn_w, btn_h), "⚙  SETTINGS",    f)
        self.btn_quit = Button(pygame.Rect(cx - btn_w // 2, 480, btn_w, btn_h), "✕  QUIT",        f)

        self.err_msg = ""

    def handle_event(self, event: pygame.event.Event):
        self.input.handle_event(event)
        if self.btn_play.handle_event(event):
            self._try_play()
        if self.btn_lb.handle_event(event):
            self.app.switch(LeaderboardScreen)
        if self.btn_cfg.handle_event(event):
            self.app.switch(SettingsScreen)
        if self.btn_quit.handle_event(event):
            pygame.quit(); sys.exit()
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            self._try_play()

    def _try_play(self):
        name = self.input.text.strip()
        if not name:
            self.err_msg = "Please enter a username first."
            return
        self.app.username  = name
        self.app.player_id = db.get_or_create_player(name)
        self.app.personal_best = db.get_personal_best(self.app.player_id) if self.app.player_id else 0
        self.app.switch(GameScreen)

    def draw(self, surface: pygame.Surface):
        tick = pygame.time.get_ticks()
        draw_bg(surface, tick)

        f = self.app.fonts
        # Title
        title = f["xl"].render("🐍 SNAKE", True, HUD_ACCENT)
        surface.blit(title, title.get_rect(center=(WINDOW_WIDTH // 2, 120)))
        sub = f["sm"].render("TSIS-3  Edition", True, GRAY)
        surface.blit(sub, sub.get_rect(center=(WINDOW_WIDTH // 2, 175)))

        # Username input
        surface.blit(self.username_label, self.username_label.get_rect(
            bottomleft=(WINDOW_WIDTH // 2 - 160, 220)))
        self.input.draw(surface, tick)

        self.btn_play.draw(surface)
        self.btn_lb.draw(surface)
        self.btn_cfg.draw(surface)
        self.btn_quit.draw(surface)

        if self.err_msg:
            err = f["sm"].render(self.err_msg, True, RED)
            surface.blit(err, err.get_rect(center=(WINDOW_WIDTH // 2, 280)))


# ─── Game Screen ───────────────────────────────────────────────────────────

class GameScreen(ScreenBase):
    def __init__(self, app: "App"):
        super().__init__(app)
        self.scene = GameScene(app.settings, personal_best=app.personal_best)
        self._last_step = pygame.time.get_ticks()

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.app.switch(MainMenuScreen)
        self.scene.handle_event(event)

    def update(self):
        now  = pygame.time.get_ticks()
        step = int(1000 / max(self.scene.fps, 1))
        if now - self._last_step >= step:
            self._last_step = now
            self.scene.step()

        if self.scene.game_over_flag:
            # persist result
            if self.app.player_id:
                db.save_session(self.app.player_id, self.scene.score, self.scene.level)
                new_best = db.get_personal_best(self.app.player_id)
                self.app.personal_best = new_best
            self.app.last_score = self.scene.score
            self.app.last_level = self.scene.level
            self.app.switch(GameOverScreen)

    def draw(self, surface: pygame.Surface):
        self.scene.draw(surface)


# ─── Game Over Screen ──────────────────────────────────────────────────────

class GameOverScreen(ScreenBase):
    def __init__(self, app: "App"):
        super().__init__(app)
        f   = app.fonts
        cx  = WINDOW_WIDTH // 2
        btn_w, btn_h = 220, 48
        self.btn_retry = Button(pygame.Rect(cx - btn_w - 10, 440, btn_w, btn_h), "↺  RETRY",      f)
        self.btn_menu  = Button(pygame.Rect(cx + 10,          440, btn_w, btn_h), "⌂  MAIN MENU", f)

    def handle_event(self, event: pygame.event.Event):
        if self.btn_retry.handle_event(event):
            self.app.switch(GameScreen)
        if self.btn_menu.handle_event(event):
            self.app.switch(MainMenuScreen)

    def draw(self, surface: pygame.Surface):
        tick = pygame.time.get_ticks()
        draw_bg(surface, tick)
        f  = self.app.fonts
        cx = WINDOW_WIDTH // 2

        title = f["xl"].render("GAME  OVER", True, RED)
        surface.blit(title, title.get_rect(center=(cx, 160)))

        lines = [
            (f"Score:         {self.app.last_score:06d}", YELLOW),
            (f"Level reached: {self.app.last_level}",     LIGHT_GRAY),
            (f"Personal best: {self.app.personal_best:06d}", HUD_ACCENT),
        ]
        for i, (text, color) in enumerate(lines):
            surf = f["md"].render(text, True, color)
            surface.blit(surf, surf.get_rect(center=(cx, 270 + i * 50)))

        self.btn_retry.draw(surface)
        self.btn_menu.draw(surface)


# ─── Leaderboard Screen ────────────────────────────────────────────────────

class LeaderboardScreen(ScreenBase):
    def __init__(self, app: "App"):
        super().__init__(app)
        f = app.fonts
        self.btn_back = Button(pygame.Rect(WINDOW_WIDTH // 2 - 100, 590, 200, 42), "← BACK", f)
        self.rows = db.get_top10()

    def handle_event(self, event: pygame.event.Event):
        if self.btn_back.handle_event(event):
            self.app.switch(MainMenuScreen)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.app.switch(MainMenuScreen)

    def draw(self, surface: pygame.Surface):
        tick = pygame.time.get_ticks()
        draw_bg(surface, tick)
        f  = self.app.fonts
        cx = WINDOW_WIDTH // 2

        title = f["lg"].render("🏆  TOP 10  SCORES", True, YELLOW)
        surface.blit(title, title.get_rect(center=(cx, 50)))

        # Header row
        hdrs = ["#", "Username", "Score", "Level", "Date"]
        col_x = [40, 100, 340, 470, 560]
        header_y = 105
        for hdr, hx in zip(hdrs, col_x):
            h = f["sm"].render(hdr, True, HUD_ACCENT)
            surface.blit(h, (hx, header_y))
        pygame.draw.line(surface, BTN_BORDER, (30, 128), (WINDOW_WIDTH - 30, 128), 1)

        if not self.rows:
            msg = f["md"].render("No records yet — play a game!", True, GRAY)
            surface.blit(msg, msg.get_rect(center=(cx, 300)))
        else:
            for i, row in enumerate(self.rows):
                y    = 140 + i * 44
                bg   = (25, 30, 50) if i % 2 == 0 else (18, 22, 38)
                row_rect = pygame.Rect(30, y - 4, WINDOW_WIDTH - 60, 38)
                pygame.draw.rect(surface, bg, row_rect, border_radius=4)

                # highlight current player
                if self.app.username and row.get("username") == self.app.username:
                    pygame.draw.rect(surface, (60, 80, 30), row_rect, border_radius=4)

                rank_color = [YELLOW, LIGHT_GRAY, (205, 127, 50)][min(i, 2)]  # gold/silver/bronze for top3
                vals = [
                    (str(row["rank"]), rank_color),
                    (str(row["username"])[:14], WHITE),
                    (str(row["score"]), YELLOW),
                    (str(row["level_reached"]), LIGHT_GRAY),
                    (str(row.get("played_at", ""))[:10], GRAY),
                ]
                for (val, col), hx in zip(vals, col_x):
                    s = f["xs"].render(val, True, col)
                    surface.blit(s, (hx, y + 8))

        self.btn_back.draw(surface)


# ─── Settings Screen ───────────────────────────────────────────────────────

class SettingsScreen(ScreenBase):
    COLORS = {
        "Green":   [50, 200, 50],
        "Cyan":    [0,  210, 210],
        "Orange":  [255, 160, 0],
        "Yellow":  [255, 220, 0],
        "Purple":  [150, 60, 200],
        "White":   [220, 220, 220],
        "Red":     [220, 40, 40],
    }

    def __init__(self, app: "App"):
        super().__init__(app)
        # Work on a copy
        self.cfg = dict(app.settings)
        f = app.fonts
        cx = WINDOW_WIDTH // 2

        self.btn_toggle_grid  = Button(pygame.Rect(cx + 20, 180, 160, 42), self._grid_lbl(),    f)
        self.btn_toggle_sound = Button(pygame.Rect(cx + 20, 260, 160, 42), self._sound_lbl(),   f)

        # colour picker buttons
        self._color_buttons: list[tuple[str, pygame.Rect]] = []
        keys = list(self.COLORS.keys())
        bw, bh = 90, 36
        for i, name in enumerate(keys):
            col_i = i % 4
            row_i = i // 4
            rx = 80 + col_i * (bw + 12)
            ry = 360 + row_i * (bh + 10)
            self._color_buttons.append((name, pygame.Rect(rx, ry, bw, bh)))

        self.btn_save = Button(pygame.Rect(cx - 120, 540, 240, 48), "💾  SAVE & BACK", f)

    def _grid_lbl(self):
        return "Grid: ON" if self.cfg.get("grid_overlay") else "Grid: OFF"

    def _sound_lbl(self):
        return "Sound: ON" if self.cfg.get("sound") else "Sound: OFF"

    def handle_event(self, event: pygame.event.Event):
        if self.btn_toggle_grid.handle_event(event):
            self.cfg["grid_overlay"] = not self.cfg.get("grid_overlay", False)
            self.btn_toggle_grid.label = self._grid_lbl()
        if self.btn_toggle_sound.handle_event(event):
            self.cfg["sound"] = not self.cfg.get("sound", True)
            self.btn_toggle_sound.label = self._sound_lbl()
        for name, rect in self._color_buttons:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if rect.collidepoint(event.pos):
                    self.cfg["snake_color"] = self.COLORS[name]
        if self.btn_save.handle_event(event):
            sm.save(self.cfg)
            self.app.settings = self.cfg
            self.app.switch(MainMenuScreen)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.app.switch(MainMenuScreen)

    def draw(self, surface: pygame.Surface):
        tick = pygame.time.get_ticks()
        draw_bg(surface, tick)
        f  = self.app.fonts
        cx = WINDOW_WIDTH // 2

        title = f["lg"].render("⚙  SETTINGS", True, WHITE)
        surface.blit(title, title.get_rect(center=(cx, 60)))

        # Grid toggle label
        lbl = f["md"].render("Grid overlay:", True, LIGHT_GRAY)
        surface.blit(lbl, (80, 192))
        self.btn_toggle_grid.draw(surface)

        # Sound toggle label
        lbl2 = f["md"].render("Sound:",        True, LIGHT_GRAY)
        surface.blit(lbl2, (80, 272))
        self.btn_toggle_sound.draw(surface)

        # Colour picker
        color_lbl = f["md"].render("Snake colour:", True, LIGHT_GRAY)
        surface.blit(color_lbl, (80, 328))

        current = tuple(self.cfg.get("snake_color", [50, 200, 50]))
        for name, rect in self._color_buttons:
            rgb   = tuple(self.COLORS[name])
            sel   = (rgb == current)
            pygame.draw.rect(surface, rgb, rect, border_radius=6)
            border = WHITE if sel else GRAY
            bw = 3 if sel else 1
            pygame.draw.rect(surface, border, rect, bw, border_radius=6)
            txt = f["xs"].render(name, True, BLACK if sum(rgb) > 400 else WHITE)
            surface.blit(txt, txt.get_rect(center=rect.center))

        self.btn_save.draw(surface)


# ---------------------------------------------------------------------------
# App (screen manager)
# ---------------------------------------------------------------------------

class App:
    def __init__(self):
        pygame.init()
        self.screen  = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock   = pygame.time.Clock()
        self.fonts   = make_fonts()

        self.settings      = sm.load()
        self.username: str = ""
        self.player_id: int | None = None
        self.personal_best: int = 0
        self.last_score: int = 0
        self.last_level: int = 1

        db.init_db()

        self.current_screen: ScreenBase = MainMenuScreen(self)

    def switch(self, screen_cls, **kwargs):
        self.current_screen = screen_cls(self, **kwargs)

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                self.current_screen.handle_event(event)

            self.current_screen.update()
            self.current_screen.draw(self.screen)
            pygame.display.flip()
            self.clock.tick(60)   # render at 60 fps; game steps at self.scene.fps


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    App().run()