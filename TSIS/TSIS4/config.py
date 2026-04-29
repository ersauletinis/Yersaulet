# config.py — Central constants for Snake Game TSIS3
 
import pygame
 
# Window
WINDOW_WIDTH  = 800
WINDOW_HEIGHT = 650
TITLE         = "Snake Game"
 
# Grid
CELL_SIZE  = 20
GRID_COLS  = (WINDOW_WIDTH)  // CELL_SIZE   # 40
GRID_ROWS  = (WINDOW_HEIGHT - 100) // CELL_SIZE  # 27  (top 100px = HUD)
 
HUD_HEIGHT = 100   # pixels reserved at the top for score / level / power-up info
 
# Frame-rate / speed
BASE_FPS         = 10          # cells per second at level 1
FPS_INCREMENT    = 1           # extra FPS per level
MAX_FPS          = 25
 
SPEED_BOOST_MULT = 1.8         # multiplier when speed-boost active
SLOW_MOTION_MULT = 0.5         # multiplier when slow-motion active
POWERUP_DURATION = 5_000       # ms
POWERUP_SPAWN_TIMEOUT = 8_000  # ms before a powerup disappears
 
# Food
FOOD_DISAPPEAR_MS   = 8_000    # weighted/normal food timeout
POISON_CHANCE       = 0.20     # 20 % of food spawns are poison
WEIGHTED_FOOD_CHANCE= 0.25     # 25 % chance a normal spawn is "weighted" (worth more)
 
# Obstacles — start at level 3
OBSTACLE_START_LEVEL = 3
OBSTACLES_PER_LEVEL  = 4       # new walls added each level
 
# Colours (R, G, B)
BLACK       = (  0,   0,   0)
WHITE       = (255, 255, 255)
DARK_GRAY   = ( 30,  30,  30)
GRAY        = ( 80,  80,  80)
LIGHT_GRAY  = (180, 180, 180)
GREEN       = ( 50, 200,  50)
DARK_GREEN  = ( 30, 130,  30)
RED         = (220,  40,  40)
DARK_RED    = (120,   0,   0)   # poison food
ORANGE      = (255, 160,   0)
YELLOW      = (255, 220,   0)
BLUE        = ( 40, 130, 220)
CYAN        = (  0, 210, 210)
PURPLE      = (150,  60, 200)
MAGENTA     = (220,  60, 200)
BROWN       = (139,  69,  19)
 
# Food colours
FOOD_COLOR          = (220, 50,  50)   # normal food (red)
WEIGHTED_FOOD_COLOR = (255, 200,  0)   # golden food
POISON_COLOR        = (120,  0,   0)   # dark red
 
# Power-up colours
POWERUP_COLORS = {
    "speed_boost": (255, 200,   0),
    "slow_motion": (  0, 180, 255),
    "shield":      (200,   0, 255),
}
 
OBSTACLE_COLOR  = (100, 100, 110)
OBSTACLE_BORDER = ( 60,  60,  70)
 
# HUD
HUD_BG      = ( 15,  15,  25)
HUD_TEXT    = (220, 220, 220)
HUD_ACCENT  = (  0, 200, 120)
 
# Menu colours
MENU_BG     = ( 10,  12,  20)
BTN_NORMAL  = ( 30,  35,  55)
BTN_HOVER   = ( 50,  60,  90)
BTN_TEXT    = (220, 230, 255)
BTN_BORDER  = ( 80,  90, 140)
 
# Fonts (loaded at runtime)
FONT_LARGE  = None
FONT_MEDIUM = None
FONT_SMALL  = None