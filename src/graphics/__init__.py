from functools import cache
import pygame, os
import platform
from graphics.floating_hint_text import draw_floating_hint_texts, add_floating_text_hint, FloatingHintText # Make draw_floating_hint_texts available in this module

if platform.system() == "Windows":
    import ctypes
    ctypes.windll.user32.SetProcessDPIAware()

pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()

from constants import WIDTH, HEIGHT, TILE_SIZE

GIANT_FONT = pygame.font.Font(os.path.join("assets", "NotoSans-SemiBold.ttf"), 96)
BIG_FONT = pygame.font.SysFont("Consolas", 30)
FONT = pygame.font.SysFont("Consolas", 24)
SMALL_FONT = pygame.font.SysFont("Consolas", 20)
WIN = pygame.display.set_mode((WIDTH, HEIGHT))

WHITE_IMAGE = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
WHITE_IMAGE.fill('white')
WHITE_IMAGE.set_alpha(64)

@cache
def small_font_render(text, color='white'):
    return SMALL_FONT.render(text, True, color)
@cache
def normal_font_render(text, color='white'):
    return FONT.render(text, True, color)
@cache
def big_font_render(text, color='white'):
    return BIG_FONT.render(text, True, color)
@cache
def giant_font_render(text, color='white'):
    return GIANT_FONT.render(text, True, color)

TOOLTIP_BACKGROUND_COLOR = (0, 0, 0)
TOOLTIP_PADDING = 5
TOOLTIP_WINDOW_MARGIN = 20
TOOLTIP_BORDER_RADIUS = 8

def draw_tooltip(win, pos, text):
    x = pos[0] + 5
    y = pos[1] + 5
    font = normal_font_render(text)
    tooltip_x = min(max(TOOLTIP_WINDOW_MARGIN, x), WIDTH - font.get_width() - TOOLTIP_WINDOW_MARGIN)
    tooltip_y = min(max(TOOLTIP_WINDOW_MARGIN, y), HEIGHT - font.get_height() - TOOLTIP_WINDOW_MARGIN)
    width = font.get_width() + TOOLTIP_PADDING * 2
    height = font.get_height() + TOOLTIP_PADDING * 2
    pygame.draw.rect(win, TOOLTIP_BACKGROUND_COLOR, (tooltip_x, tooltip_y, width, height), border_radius=TOOLTIP_BORDER_RADIUS)
    win.blit(font, (tooltip_x + TOOLTIP_PADDING, tooltip_y + TOOLTIP_PADDING))

deferred_drawing_queue = []
def draw_deferred(func):
    deferred_drawing_queue.append(func)
def draw_all_deferred():
    for item in deferred_drawing_queue:
        item()
    deferred_drawing_queue.clear()