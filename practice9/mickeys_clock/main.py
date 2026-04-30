"""
Mickey's Music Player
=====================
Keyboard controls:
  P  — Play / Resume
  S  — Stop
  SPACE — Pause / Resume toggle
  N  — Next track
  B  — Previous (Back) track
  Q  — Quit
"""
 
import pygame
import math
import os
import sys
 
# Allow running from any working directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
 
from player import MusicPlayer
 
# ------------------------------------------------------------------ #
#  Constants                                                           #
# ------------------------------------------------------------------ #
 
WIDTH, HEIGHT = 800, 520
FPS = 60
MUSIC_DIR = os.path.join(BASE_DIR, "music")
 
# Palette — dark retro theme
BG          = (15,  12,  20)
PANEL       = (28,  24,  38)
ACCENT      = (255, 80,  120)   # hot pink / red
ACCENT2     = (80,  200, 255)   # cyan
TEXT_MAIN   = (240, 235, 250)
TEXT_DIM    = (120, 110, 140)
BAR_BG      = (50,  44,  64)
BAR_FG      = ACCENT
DOT         = (255, 255, 255)
 
# ------------------------------------------------------------------ #
#  Drawing helpers                                                     #
# ------------------------------------------------------------------ #
 
def draw_rounded_rect(surf, color, rect, radius, alpha=255):
    s = pygame.Surface((rect[2], rect[3]), pygame.SRCALPHA)
    pygame.draw.rect(s, (*color, alpha), (0, 0, rect[2], rect[3]), border_radius=radius)
    surf.blit(s, (rect[0], rect[1]))
 
 
def draw_text_centered(surf, text, font, color, cx, cy):
    rendered = font.render(text, True, color)
    r = rendered.get_rect(center=(cx, cy))
    surf.blit(rendered, r)
    return r
 
 
def draw_vinyl(surf, cx, cy, radius, angle, playing):
    """Spinning vinyl disc."""
    # Outer disc
    pygame.draw.circle(surf, (35, 30, 48), (cx, cy), radius)
    # Groove rings
    for r in range(radius - 8, 20, -12):
        alpha = 60 if playing else 30
        pygame.gfxdraw_circle_aa(surf, cx, cy, r, (*TEXT_DIM, alpha))
    # Spinning label
    label_r = radius // 3
    pygame.draw.circle(surf, ACCENT, (cx, cy), label_r)
    pygame.draw.circle(surf, BG, (cx, cy), label_r - 6)
    # Needle arm indicator dot
    dot_x = int(cx + (label_r - 2) * math.cos(math.radians(angle)))
    dot_y = int(cy + (label_r - 2) * math.sin(math.radians(angle)))
    pygame.draw.circle(surf, DOT, (dot_x, dot_y), 4)
    # Centre hole
    pygame.draw.circle(surf, BG, (cx, cy), 5)
 
 
def pygame_gfxdraw_circle_aa_fallback(surf, cx, cy, r, color):
    try:
        import pygame.gfxdraw
        pygame.gfxdraw.aacircle(surf, cx, cy, r, color)
    except Exception:
        pygame.draw.circle(surf, color[:3], (cx, cy), r, 1)
 
 
# Monkey-patch so draw_vinyl works without gfxdraw
pygame_gfxdraw_circle_aa_fallback.__name__ = "pygame_gfxdraw_circle_aa_fallback"
 
 
def pygame_gfxdraw_circle_aa(surf, cx, cy, r, color):
    pygame_gfxdraw_circle_aa_fallback(surf, cx, cy, r, color)
 
 
# Override the helper used inside draw_vinyl
globals()["pygame_gfxdraw_circle_aa"] = \
    lambda s, cx, cy, r, c: pygame_gfxdraw_circle_aa_fallback(s, cx, cy, r, c)
globals()["pygame_gfxdraw_circle_aa_fallback"] = pygame_gfxdraw_circle_aa_fallback
 
# Rebind name used in draw_vinyl
def pygame_gfxdraw_circle_aa(surf, cx, cy, r, color):  # noqa: F811
    pygame_gfxdraw_circle_aa_fallback(surf, cx, cy, r, color)
 
 
def draw_progress_bar(surf, x, y, w, h, fraction, radius=6):
    draw_rounded_rect(surf, BAR_BG, (x, y, w, h), radius)
    fill_w = max(radius * 2, int(w * fraction))
    draw_rounded_rect(surf, BAR_FG, (x, y, fill_w, h), radius)
    # Playhead dot
    dot_x = x + fill_w
    dot_y = y + h // 2
    pygame.draw.circle(surf, DOT, (dot_x, dot_y), h)
 
 
def draw_key_hint(surf, font_sm, keys_actions, x, y, gap=52):
    for i, (key, action) in enumerate(keys_actions):
        kx = x + i * gap
        # Key cap
        draw_rounded_rect(surf, PANEL, (kx - 2, y - 2, 34, 28), 6)
        pygame.draw.rect(surf, TEXT_DIM, (kx - 2, y - 2, 34, 28), 1, border_radius=6)
        k_surf = font_sm.render(key, True, ACCENT2)
        surf.blit(k_surf, (kx + 3, y + 3))
        # Label below
        lbl = font_sm.render(action, True, TEXT_DIM)
        surf.blit(lbl, (kx - 4, y + 32))
 
 
# ------------------------------------------------------------------ #
#  Main                                                                #
# ------------------------------------------------------------------ #
 
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("♫  Music Player")
    clock = pygame.time.Clock()
 
    # Fonts
    font_title  = pygame.font.SysFont("couriernew", 22, bold=True)
    font_track  = pygame.font.SysFont("couriernew", 28, bold=True)
    font_sub    = pygame.font.SysFont("couriernew", 16)
    font_sm     = pygame.font.SysFont("couriernew", 13, bold=True)
    font_status = pygame.font.SysFont("couriernew", 14, bold=True)
 
    player = MusicPlayer(MUSIC_DIR)
 
    vinyl_angle = 0.0   # degrees, spins when playing
    spin_speed  = 1.2   # degrees per frame
 
    # Progress bar simulation (we track time manually since mixer.get_pos resets on pause)
    elapsed_ms   = 0
    duration_ms  = 180_000  # default 3 min; no easy way to get actual duration without mutagen
    last_tick_ms = pygame.time.get_ticks()
 
    running = True
    while running:
        dt_ms = pygame.time.get_ticks() - last_tick_ms
        last_tick_ms = pygame.time.get_ticks()
 
        # ---- Events ------------------------------------------------- #
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
 
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    running = False
                elif event.key == pygame.K_p:
                    player.play()
                    elapsed_ms = 0
                elif event.key == pygame.K_s:
                    player.stop()
                    elapsed_ms = 0
                elif event.key == pygame.K_SPACE:
                    if player.is_playing:
                        player.pause()
                    else:
                        player.play()
                elif event.key == pygame.K_n:
                    player.next_track()
                    elapsed_ms = 0
                elif event.key == pygame.K_b:
                    player.prev_track()
                    elapsed_ms = 0
 
        # ---- Update -------------------------------------------------- #
        player.check_end()
 
        if player.is_playing:
            elapsed_ms  += dt_ms
            vinyl_angle = (vinyl_angle + spin_speed) % 360
        if elapsed_ms > duration_ms:
            elapsed_ms = duration_ms
 
        progress = elapsed_ms / duration_ms
 
        # ---- Draw ---------------------------------------------------- #
        screen.fill(BG)
 
        # Top header bar
        draw_rounded_rect(screen, PANEL, (0, 0, WIDTH, 70), 0)
        draw_text_centered(screen, "♫  MUSIC  PLAYER", font_title, ACCENT, WIDTH // 2, 35)
 
        # Vinyl disc  (left side)
        vinyl_cx, vinyl_cy = 190, 260
        vinyl_r = 140
        draw_vinyl(screen, vinyl_cx, vinyl_cy, vinyl_r, vinyl_angle, player.is_playing)
 
        # Right panel
        rx, ry = 370, 90
        rw, rh = WIDTH - rx - 20, HEIGHT - ry - 20
        draw_rounded_rect(screen, PANEL, (rx, ry, rw, rh), 18)
 
        # Track number
        draw_text_centered(screen, player.track_number(), font_sub, TEXT_DIM,
                           rx + rw // 2, ry + 28)
 
        # Track name (truncate if long)
        name = player.track_name()
        if len(name) > 22:
            name = name[:20] + "…"
        draw_text_centered(screen, name, font_track, TEXT_MAIN,
                           rx + rw // 2, ry + 72)
 
        # Status badge
        status = player.status()
        status_color = ACCENT if status == "PLAYING" else (ACCENT2 if status == "PAUSED" else TEXT_DIM)
        draw_rounded_rect(screen, BG, (rx + rw // 2 - 52, ry + 100, 104, 26), 13)
        draw_text_centered(screen, f"● {status}", font_status, status_color,
                           rx + rw // 2, ry + 113)
 
        # Progress bar
        bar_x = rx + 20
        bar_y = ry + 148
        bar_w = rw - 40
        draw_progress_bar(screen, bar_x, bar_y, bar_w, 8, progress)
 
        # Time labels
        elapsed_s = elapsed_ms // 1000
        total_s   = duration_ms // 1000
        time_str  = f"{elapsed_s // 60:02d}:{elapsed_s % 60:02d}  /  {total_s // 60:02d}:{total_s % 60:02d}"
        draw_text_centered(screen, time_str, font_sub, TEXT_DIM,
                           rx + rw // 2, ry + 178)
 
        # Playlist mini-list (show up to 3 tracks around current)
        list_y = ry + 205
        pygame.draw.line(screen, BAR_BG, (rx + 20, list_y - 10), (rx + rw - 20, list_y - 10))
        for i, path in enumerate(player.tracks[:5]):
            tname = os.path.splitext(os.path.basename(path))[0]
            if len(tname) > 24:
                tname = tname[:22] + "…"
            is_cur = (i == player.current_index)
            col    = ACCENT if is_cur else TEXT_DIM
            prefix = "▶ " if is_cur else "  "
            lbl    = font_sm.render(prefix + tname, True, col)
            screen.blit(lbl, (rx + 28, list_y + i * 22))
 
        # Keyboard hints (bottom strip)
        hints = [("P", "Play"), ("S", "Stop"), ("SPC", "Pause"), ("N", "Next"), ("B", "Back"), ("Q", "Quit")]
        draw_key_hint(screen, font_sm, hints, 40, HEIGHT - 68)
 
        pygame.display.flip()
        clock.tick(FPS)
 
    player.stop()
    pygame.quit()
 
 
if __name__ == "__main__":
    main()
 