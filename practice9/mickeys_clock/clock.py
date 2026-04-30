import pygame
import datetime
import math

pygame.init()
screen = pygame.display.set_mode((1200, 700))
WHITE = (255, 255, 255)

image_surface = pygame.image.load('mickeys_clock/images/clock.png')
mickey  = pygame.image.load('mickeys_clock/images/mikkey.png')
hand_l  = pygame.image.load('mickeys_clock/images/hand_left_centered.png')
hand_r  = pygame.image.load('mickeys_clock/images/hand_right_centered.png')

resized_image = pygame.transform.scale(image_surface, (800, 600))
res_mickey    = pygame.transform.scale(mickey, (350, 350))
hand_l_base   = pygame.transform.scale(hand_l, (200, 200))
hand_r_base   = pygame.transform.scale(hand_r, (200, 200))

CLOCK_CENTER = (600, 340)
W, H = 1200, 700

# Отдельный surface для вращения — точно как в AnalogClock
rotation_surface = pygame.Surface((W, H), pygame.SRCALPHA)

def draw_hand(surface, rot_surf, hand_img, angle_deg):
    """
    Вращает руку вокруг ОСНОВАНИЯ (нижний центр PNG),
    как __draw_hand в AnalogClock через rotation_surface.
    angle_deg: 0 = 12 часов, растёт по часовой стрелке.
    """
    hand_w, hand_h = hand_img.get_size()
    cx, cy = CLOCK_CENTER

    # Рисуем руку так, чтобы её основание было в центре циферблата
    # Основание = нижний центр PNG → смещаем вверх на hand_h
    rect_x = cx - hand_w // 2
    rect_y = cy - hand_h  # основание руки на уровне центра

    rot_surf.fill((0, 0, 0, 0))
    rot_surf.blit(hand_img, (rect_x, rect_y))

    # Вращаем вокруг центра surface (= центра циферблата)
    rotated = pygame.transform.rotate(rot_surf, -angle_deg)
    rotated_rect = rotated.get_rect(center=CLOCK_CENTER)
    surface.blit(rotated, rotated_rect)

clock_tick = pygame.time.Clock()
done = False

while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True

    now = datetime.datetime.now()
    h = now.hour % 12
    m = now.minute
    s = now.second

    minutes_angle = m * 6 + s * 0.1
    hours_angle   = h * 30 + m * 0.5

    screen.fill(WHITE)

    # 1. Циферблат
    image_rect = resized_image.get_rect(center=CLOCK_CENTER)
    screen.blit(resized_image, image_rect)

    # 2. Стрелки — часовая под минутной
    draw_hand(screen, rotation_surface, hand_r_base, hours_angle)
    draw_hand(screen, rotation_surface, hand_l_base, minutes_angle)

    # 3. Микки поверх всего
    mic_rect = res_mickey.get_rect(center=CLOCK_CENTER)
    screen.blit(res_mickey, mic_rect)

    pygame.display.flip()
    clock_tick.tick(60)

pygame.quit()