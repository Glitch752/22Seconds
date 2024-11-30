from typing import Literal
import pygame

from graphics import get_height, get_width

class FloatingHintText:
    start_time: float
    surface: pygame.Surface
    x: int
    y: int
    vertical_movement: int
    stay_time: float
    fade_time: float
    fixed_in_world: bool
    manually_finished: bool
    alignment: Literal["left", "center", "right"]
    def __init__(
        self,
        text, pos, color = "white",
        vertical_movement = -30,
        stay_time = 0.5, fade_time = 0.5,
        fixed_in_world=True,
        alignment="center"
    ):
        from graphics import small_font_render
        self.start_time = pygame.time.get_ticks() / 1000 # Seconds
        sfr = small_font_render(text, color)
        self.surface = pygame.Surface((sfr.get_width() + 2, sfr.get_height() + 2), pygame.SRCALPHA)
        self.surface.blit(small_font_render(text, 'black'), (2, 2))
        self.surface.blit(sfr, (0, 0))
        self.x = pos[0] # Pixels
        self.y = pos[1] # Pixels
        self.vertical_movement = vertical_movement # Pixels per second
        self.stay_time = stay_time # Seconds
        self.fade_time = fade_time # Seconds
        self.fixed_in_world = fixed_in_world
        self.manually_finished = False
        self.alignment = alignment
    def is_complete(self):
        if self.manually_finished:
            return True
        time = pygame.time.get_ticks() / 1000
        elapsed = time - self.start_time
        return elapsed > self.stay_time + self.fade_time
    def draw(self, win: pygame.Surface, camera_pos: tuple[int, int]):
        time = pygame.time.get_ticks() / 1000
        elapsed = time - self.start_time
        offset = 0
        if self.alignment == "center":
            offset = self.surface.get_width() // 2
        elif self.alignment == "right":
            offset = self.surface.get_width()
        x_position = self.x - offset
        y_position = self.y + elapsed * self.vertical_movement
        if self.fixed_in_world:
            x_position -= camera_pos[0]
            y_position -= camera_pos[1]
            x_position += get_width() // 2
            y_position += get_height() // 2
        opacity = 255
        if elapsed > self.stay_time:
            opacity = 255 - int(255 * ((elapsed - self.stay_time) / self.fade_time))
        self.surface.set_alpha(opacity)
        win.blit(self.surface, (x_position, y_position))

floating_hint_texts: list[FloatingHintText] = []

def add_floating_text_hint(hint):
    floating_hint_texts.append(hint)
def draw_floating_hint_texts(win: pygame.Surface, camera_pos: tuple[int, int]):
    global floating_hint_texts
    i = 0
    while i < len(floating_hint_texts):
        floating_hint_text = floating_hint_texts[i]
        if floating_hint_text.is_complete():
            floating_hint_texts.pop(i)
            i -= 1
        floating_hint_text.draw(win, camera_pos)
        i += 1