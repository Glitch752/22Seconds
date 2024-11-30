from functools import cache
import pygame, os
from graphics.floating_hint_text import draw_floating_hint_texts, add_floating_text_hint, FloatingHintText # Make draw_floating_hint_texts available in this module
from constants import DEFAULT_WIDTH, DEFAULT_HEIGHT, TILE_SIZE

GIANT_FONT = pygame.font.Font(os.path.join("assets", "NotoSans-SemiBold.ttf"), 96)
BIG_FONT = pygame.font.SysFont("Consolas", 30)
FONT = pygame.font.SysFont("Consolas", 24)
SMALL_FONT = pygame.font.SysFont("Consolas", 20)
WIN = pygame.display.set_mode((DEFAULT_WIDTH, DEFAULT_HEIGHT), pygame.RESIZABLE, vsync=1)

def get_width():
    """Get the current width of the window."""
    return WIN.get_width()
def get_height():
    """Get the current height of the window."""
    return WIN.get_height()

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
TOOLTIP_LINE_SPACING = -2

@cache
def make_transparent_rect_surface(color: tuple[int, int, int], rect: tuple[int, int, int, int], alpha: int, border_radius: int = 0):
    surface = pygame.Surface((rect[2], rect[3]), pygame.SRCALPHA)
    surface.fill((0, 0, 0, 0))
    pygame.draw.rect(surface, color + (alpha,), (0, 0, rect[2], rect[3]), border_radius=border_radius)
    return surface

def transparent_rect(win: pygame.Surface, color: tuple[int, int, int], rect: tuple[int, int, int, int], alpha: int, border_radius: int = 0):
    win.blit(make_transparent_rect_surface(color, rect, alpha, border_radius), (rect[0], rect[1]))

type TextLine = str | tuple[str, str]
def draw_tooltip(win: pygame.Surface, pos: tuple[int, int], text: list[TextLine] | TextLine):
    """Half-baked text formatting system... Sorry for the mess."""
    if isinstance(text, str):
        text = [text]
    
    font_lines = [normal_font_render(line) if isinstance(line, str) else normal_font_render(*line) for line in text]
    max_width = max(font.get_width() for font in font_lines) + 3
    text_height = sum(font.get_height() + TOOLTIP_LINE_SPACING for font in font_lines) - TOOLTIP_LINE_SPACING
    
    x = pos[0] + TOOLTIP_PADDING
    y = pos[1] + TOOLTIP_PADDING
    # Direct toward the center of the screen
    if pos[0] > get_width() // 2:
        x -= max_width + TOOLTIP_PADDING * 2
    if pos[1] > get_height() // 2:
        y -= text_height + TOOLTIP_PADDING * 2
    
    tooltip_x = min(max(TOOLTIP_WINDOW_MARGIN, x), get_width() - max_width - TOOLTIP_WINDOW_MARGIN)
    tooltip_y = min(max(TOOLTIP_WINDOW_MARGIN, y), get_height() - text_height - TOOLTIP_WINDOW_MARGIN)
    
    width = max_width + TOOLTIP_PADDING * 2
    height = text_height + TOOLTIP_PADDING * 2
    # pygame.draw.rect(win, TOOLTIP_BACKGROUND_COLOR, (tooltip_x, tooltip_y, width, height), border_radius=TOOLTIP_BORDER_RADIUS)
    transparent_rect(win, TOOLTIP_BACKGROUND_COLOR, (tooltip_x, tooltip_y, width, height), 200, TOOLTIP_BORDER_RADIUS)
    y = tooltip_y + TOOLTIP_PADDING
    for font in font_lines:
        win.blit(font, (tooltip_x + TOOLTIP_PADDING + 3, y + 3))
        y += font.get_height() + TOOLTIP_LINE_SPACING

deferred_drawing_queue = []
def draw_deferred(func):
    deferred_drawing_queue.append(func)
def draw_all_deferred():
    for item in deferred_drawing_queue:
        item()
    deferred_drawing_queue.clear()