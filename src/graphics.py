from functools import cache
import pygame, os
pygame.init()

from constants import WIDTH, HEIGHT, TILE_SIZE

BIG_FONT = pygame.font.SysFont("Consolas", 36)
FONT = pygame.font.SysFont("Consolas", 30)
SMALL_FONT = pygame.font.SysFont("Consolas", 24)
WIN = pygame.display.set_mode((WIDTH, HEIGHT))

WHITE_IMAGE = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
WHITE_IMAGE.fill('white')
WHITE_IMAGE.set_alpha(64)

class FloatingHintText:
    def __init__(
        self,
        text, pos, color = "white",
        vertical_movement = -30,
        stay_time = 0.5, fade_time = 0.5,
        fixed_in_world=True
    ):
        self.start_time = pygame.time.get_ticks() / 1000 # Seconds
        self.surface = small_font_render(text, color)
        self.x = pos[0] # Pixels
        self.y = pos[1] # Pixels
        self.vertical_movement = vertical_movement # Pixels per second
        self.stay_time = stay_time # Seconds
        self.fade_time = fade_time # Seconds
        self.fixed_in_world = fixed_in_world
        self.manually_finished = False
    def is_complete(self):
        if self.manually_finished:
            return True
        time = pygame.time.get_ticks() / 1000
        elapsed = time - self.start_time
        return elapsed > self.stay_time + self.fade_time
    def draw(self, win: pygame.Surface, player_pos):
        time = pygame.time.get_ticks() / 1000
        elapsed = time - self.start_time
        x_position = self.x - self.surface.get_width() // 2
        y_position = self.y + elapsed * self.vertical_movement
        if self.fixed_in_world:
            x_position -= player_pos[0]
            y_position -= player_pos[1]
        opacity = 255
        if elapsed > self.stay_time:
            opacity = 255 - int(255 * ((elapsed - self.stay_time) / self.fade_time))
        self.surface.set_alpha(opacity)
        win.blit(self.surface, (x_position, y_position))

floating_hint_texts = []

@cache
def small_font_render(text, color='white'):
    return SMALL_FONT.render(text, True, color)
@cache
def normal_font_render(text, color='white'):
    return FONT.render(text, True, color)
@cache
def big_font_render(text, color='white'):
    return BIG_FONT.render(text, True, color)

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

def add_floating_text_hint(hint):
    floating_hint_texts.append(hint)
def draw_floating_hint_texts(win, player_pos):
    global floating_hint_texts
    i = 0
    while i < len(floating_hint_texts):
        floating_hint_text = floating_hint_texts[i]
        if floating_hint_text.is_complete():
            floating_hint_texts.pop(i)
            i -= 1
        floating_hint_text.draw(win, player_pos)
        i += 1

menuGFX = pygame.image.load(os.path.join("assets", "sprites", "menu.png"))

def draw_patchrect(screen, rect, graphic=menuGFX):
    
    pw = rect.w // 32
    ph = rect.h // 32
    
    for x in range(pw):
        for y in range(ph):
            ox = -1
            oy = -1

            if y == 0:
                if x == 0:
                    ox = 0
                    oy = 0
                elif x == pw - 1:
                    ox = 2
                    oy = 0
                else:
                    ox = 1
                    oy = 0
            elif y == ph - 1:
                if x == 0:
                    ox = 0
                    oy = 2
                elif x == pw - 1:
                    ox = 2
                    oy = 2
                else:
                    ox = 1
                    oy = 2
            elif x == 0:
                ox = 0
                oy = 1
            elif x == pw - 1:
                ox = 2
                oy = 1
            else:
                ox = 1
                oy = 1

            if ox != -1 and oy != -1:
                screen.blit(pygame.transform.scale(
                    graphic.subsurface((ox * 8, oy * 8, 8, 8)),
                    (32, 32)),
                    (rect.x + x * 32, rect.y + y * 32))
