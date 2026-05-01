
"""
Paint — Extended
================
Brush controls:
  R / G / B      — red / green / blue brush colour
  C              — clear canvas
  Left click     — grow brush radius
  Right click    — shrink brush radius
  Mouse drag     — freehand draw
 
Shape tools (toolbar buttons or keys):
  1  — Freehand brush (default)
  2  — Square
  3  — Right triangle
  4  — Equilateral triangle
  5  — Rhombus
 
Shape drawing:
  Click to set the first corner / centre, drag, release to finish.
 
Ctrl+W / Alt+F4 / Escape — quit
"""
 
import pygame
import math
 
# ── Constants ─────────────────────────────────────────────────────────────────
 
CANVAS_W, CANVAS_H = 1000, 560  # drawing area (wider to fit toolbar)
TOOLBAR_H          = 80          # toolbar strip at the bottom
WIN_W              = CANVAS_W
WIN_H              = CANVAS_H + TOOLBAR_H
 
# Palette
BG_CANVAS   = (18,  18,  18)
BG_TOOLBAR  = (30,  30,  30)
BORDER_COL  = (60,  60,  60)
LABEL_COL   = (200, 200, 200)
ACTIVE_COL  = (255, 220,  50)    # highlight for selected tool
 
# Shape mode identifiers
MODE_BRUSH    = 'brush'
MODE_SQUARE   = 'square'
MODE_RTRI     = 'right_triangle'
MODE_EQTRI    = 'equilateral_triangle'
MODE_RHOMBUS  = 'rhombus'
 
SHAPE_MODES = [MODE_BRUSH, MODE_SQUARE, MODE_RTRI, MODE_EQTRI, MODE_RHOMBUS]
SHAPE_KEYS  = [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5]
SHAPE_LABELS = ["1:Brush", "2:Square", "3:R.Tri", "4:EqTri", "5:Rhombus"]
 
 
# ── Shape geometry helpers ────────────────────────────────────────────────────
 
def square_points(x0, y0, x1, y1):
    """
    Return 4 corners of a square whose one corner is (x0,y0)
    and the opposite corner determines the side length (uniform).
    """
    side = max(abs(x1 - x0), abs(y1 - y0))
    sx   = side if x1 >= x0 else -side
    sy   = side if y1 >= y0 else -side
    return [(x0, y0), (x0 + sx, y0), (x0 + sx, y0 + sy), (x0, y0 + sy)]
 
 
def right_triangle_points(x0, y0, x1, y1):
    """
    Right angle at (x0, y1):
      A = (x0, y0)  — top-left
      B = (x1, y1)  — bottom-right
      C = (x0, y1)  — right-angle corner (bottom-left)
    """
    return [(x0, y0), (x1, y1), (x0, y1)]
 
 
def equilateral_triangle_points(x0, y0, x1, y1):
    """
    Base from (x0,y1) to (x1,y1); apex above centre.
    Height = base * sqrt(3)/2.
    """
    base   = abs(x1 - x0)
    height = int(base * math.sqrt(3) / 2)
    cx     = (x0 + x1) // 2
    # Apex goes upward (smaller y)
    top_y  = y1 - height
    return [(x0, y1), (x1, y1), (cx, top_y)]
 
 
def rhombus_points(x0, y0, x1, y1):
    """
    Axis-aligned rhombus inscribed in the bounding box (x0,y0)→(x1,y1).
    4 mid-edge points: top, right, bottom, left.
    """
    cx = (x0 + x1) // 2
    cy = (y0 + y1) // 2
    return [(cx, y0), (x1, cy), (cx, y1), (x0, cy)]
 
 
# ── Brush drawing (original logic preserved) ──────────────────────────────────
 
def draw_line_between(surface, index, start, end, width, color_mode):
    """
    Draw a smooth coloured line between two points using interpolated circles.
    Colour fades from dark (old) to bright (recent) based on index in trail.
    """
    c1 = max(0, min(255, 2 * index - 256))   # darker component
    c2 = max(0, min(255, 2 * index))          # brighter component
 
    if color_mode == 'blue':
        color = (c1, c1, c2)
    elif color_mode == 'red':
        color = (c2, c1, c1)
    else:  # green
        color = (c1, c2, c1)
 
    dx         = start[0] - end[0]
    dy         = start[1] - end[1]
    iterations = max(abs(dx), abs(dy))
 
    for i in range(iterations):
        progress  = i / iterations if iterations else 0
        aprogress = 1 - progress
        x = int(aprogress * start[0] + progress * end[0])
        y = int(aprogress * start[1] + progress * end[1])
        pygame.draw.circle(surface, color, (x, y), width)
 
 
# ── Toolbar ───────────────────────────────────────────────────────────────────
 
def draw_toolbar(screen, font, mode, color_mode, radius):
    """
    Draw toolbar with two rows:
      Row 1 — shape tool buttons (evenly spaced)
      Row 2 — brush info (colour, radius, hotkey hints)
    """
    # Background and separator line
    toolbar_rect = pygame.Rect(0, CANVAS_H, WIN_W, TOOLBAR_H)
    pygame.draw.rect(screen, BG_TOOLBAR, toolbar_rect)
    pygame.draw.line(screen, BORDER_COL, (0, CANVAS_H), (WIN_W, CANVAS_H), 1)
 
    # ── Row 1: tool buttons ───────────────────────────────────────────────────
    n       = len(SHAPE_LABELS)
    btn_h   = 28
    row1_y  = CANVAS_H + 8          # top padding
    padding = 8                      # gap between buttons
    total_w = WIN_W - 20             # usable width
    btn_w   = (total_w - padding * (n - 1)) // n   # equal-width buttons
 
    for i, (label, smode) in enumerate(zip(SHAPE_LABELS, SHAPE_MODES)):
        bx   = 10 + i * (btn_w + padding)
        rect = pygame.Rect(bx, row1_y, btn_w, btn_h)
 
        # Active tool gets yellow highlight
        if smode == mode:
            pygame.draw.rect(screen, ACTIVE_COL, rect, border_radius=5)
            txt_col = (20, 20, 20)
        else:
            pygame.draw.rect(screen, BORDER_COL, rect, border_radius=5)
            txt_col = LABEL_COL
 
        lbl = font.render(label, True, txt_col)
        screen.blit(lbl, (bx + (btn_w - lbl.get_width()) // 2,
                          row1_y + (btn_h - lbl.get_height()) // 2))
 
    # ── Row 2: brush info ─────────────────────────────────────────────────────
    col_map  = {'red': (220, 60, 60), 'green': (60, 200, 80), 'blue': (60, 120, 255)}
    row2_y   = CANVAS_H + 8 + btn_h + 6
 
    # Colour swatch circle
    swatch_x = 18
    swatch_y = row2_y + 8
    pygame.draw.circle(screen, col_map[color_mode], (swatch_x, swatch_y), 7)
 
    info = font.render(
        f"  Colour: {color_mode}    Radius: {radius}    "
        f"[R/G/B] change colour    [C] clear    [1-5] tools",
        True, LABEL_COL
    )
    screen.blit(info, (28, row2_y))
 
 
# ── Main ──────────────────────────────────────────────────────────────────────
 
def main():
    pygame.init()
    screen  = pygame.display.set_mode((WIN_W, WIN_H))
    pygame.display.set_caption("Paint — Extended")
    clock   = pygame.time.Clock()
    font    = pygame.font.SysFont("couriernew", 13, bold=True)
 
    # Canvas is a separate surface so toolbar doesn't get painted over
    canvas  = pygame.Surface((CANVAS_W, CANVAS_H))
    canvas.fill(BG_CANVAS)
 
    radius     = 15
    color_mode = 'green'
    mode       = MODE_BRUSH   # current tool
    points     = []           # brush trail
 
    # Shape drag state
    dragging      = False     # True while mouse button held for a shape
    drag_start    = (0, 0)    # screen position where drag began
    preview_end   = (0, 0)    # current mouse position during drag
 
    running = True
    while running:
        pressed   = pygame.key.get_pressed()
        alt_held  = pressed[pygame.K_LALT]  or pressed[pygame.K_RALT]
        ctrl_held = pressed[pygame.K_LCTRL] or pressed[pygame.K_RCTRL]
 
        for event in pygame.event.get():
            # ── Quit ──────────────────────────────────────────────────────────
            if event.type == pygame.QUIT:
                running = False
 
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w and ctrl_held:
                    running = False
                if event.key == pygame.K_F4 and alt_held:
                    running = False
                if event.key == pygame.K_ESCAPE:
                    running = False
 
                # Colour keys
                if event.key == pygame.K_r:
                    color_mode = 'red'
                elif event.key == pygame.K_g:
                    color_mode = 'green'
                elif event.key == pygame.K_b:
                    color_mode = 'blue'
                elif event.key == pygame.K_c:
                    # Clear canvas
                    canvas.fill(BG_CANVAS)
                    points = []
 
                # Tool selection keys 1-5
                for k, m in zip(SHAPE_KEYS, SHAPE_MODES):
                    if event.key == k:
                        mode   = m
                        points = []  # reset brush trail on tool switch
 
            # ── Mouse: radius change (brush mode) ─────────────────────────────
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                on_canvas = my < CANVAS_H   # ignore clicks on toolbar
 
                if on_canvas:
                    if event.button == 1:
                        radius = min(200, radius + 1)
                        if mode != MODE_BRUSH:
                            # Start shape drag
                            dragging   = True
                            drag_start = event.pos
                    elif event.button == 3:
                        radius = max(1, radius - 1)
 
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and dragging and mode != MODE_BRUSH:
                    # Commit shape to canvas
                    x0, y0 = drag_start
                    x1, y1 = event.pos
 
                    # Choose draw colour (use full brightness)
                    col_map = {
                        'red':   (220,  60,  60),
                        'green': ( 60, 200,  80),
                        'blue':  ( 60, 120, 255),
                    }
                    draw_color = col_map[color_mode]
                    lw = max(1, radius // 3)   # line width scales with brush
 
                    if mode == MODE_SQUARE:
                        pts = square_points(x0, y0, x1, y1)
                        pygame.draw.polygon(canvas, draw_color, pts, lw)
 
                    elif mode == MODE_RTRI:
                        pts = right_triangle_points(x0, y0, x1, y1)
                        pygame.draw.polygon(canvas, draw_color, pts, lw)
 
                    elif mode == MODE_EQTRI:
                        pts = equilateral_triangle_points(x0, y0, x1, y1)
                        pygame.draw.polygon(canvas, draw_color, pts, lw)
 
                    elif mode == MODE_RHOMBUS:
                        pts = rhombus_points(x0, y0, x1, y1)
                        pygame.draw.polygon(canvas, draw_color, pts, lw)
 
                    dragging = False
 
            # ── Mouse motion ──────────────────────────────────────────────────
            if event.type == pygame.MOUSEMOTION:
                mx, my = event.pos
                if my < CANVAS_H:   # only paint on canvas area
                    if mode == MODE_BRUSH and pygame.mouse.get_pressed()[0]:
                        points = (points + [event.pos])[-256:]
                    preview_end = event.pos   # update shape preview endpoint
 
        # ── Draw canvas to screen ─────────────────────────────────────────────
        screen.blit(canvas, (0, 0))
 
        # Draw brush trail onto canvas (permanent)
        if mode == MODE_BRUSH:
            i = 0
            while i < len(points) - 1:
                draw_line_between(canvas, i, points[i], points[i + 1],
                                  radius, color_mode)
                i += 1
 
        # Live preview of shape while dragging (drawn on screen, not canvas)
        if dragging and mode != MODE_BRUSH:
            x0, y0 = drag_start
            x1, y1 = preview_end
            col_map = {
                'red':   (220,  60,  60),
                'green': ( 60, 200,  80),
                'blue':  ( 60, 120, 255),
            }
            prev_color = (*col_map[color_mode][:3],)
            lw = max(1, radius // 3)
 
            if mode == MODE_SQUARE:
                pts = square_points(x0, y0, x1, y1)
            elif mode == MODE_RTRI:
                pts = right_triangle_points(x0, y0, x1, y1)
            elif mode == MODE_EQTRI:
                pts = equilateral_triangle_points(x0, y0, x1, y1)
            elif mode == MODE_RHOMBUS:
                pts = rhombus_points(x0, y0, x1, y1)
            else:
                pts = []
 
            if len(pts) >= 3:
                # Draw dashed preview using a transparent overlay
                overlay = canvas.copy()
                pygame.draw.polygon(overlay, prev_color, pts, lw)
                screen.blit(overlay, (0, 0))
 
        # ── Toolbar ───────────────────────────────────────────────────────────
        draw_toolbar(screen, font, mode, color_mode, radius)
 
        pygame.display.flip()
        clock.tick(60)
 
    pygame.quit()
 
 
main()