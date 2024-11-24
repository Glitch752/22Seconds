import pygame
from constants import WIDTH
from graphics import small_font_render, normal_font_render
from items import ITEM_SLOT_BORDER_RADIUS, SLOT_BACKGROUND
import os
import random

speaking_sounds = [
    pygame.mixer.Sound(os.path.join("assets", "audio", f"speak_{str(sound).rjust(2, '0')}.wav")) for sound in range(1, 15)
]

class DialogueManager:
    def __init__(self) -> None:
        self.queue = []
        self.lines = []
        self.current_char = 0
        self.current_line = 0
        self.timer = 0
        self.done = False

    def queue_dialogue(self, lines):
        self.queue.append(lines)
    
    def on_confirm(self):
        # TODO: If still speaking, finish the line instead of skipping it.
        
        self.done = False
        self.current_char = 0
        self.current_line = 0
        self.lines.clear()
        if len(self.queue):
            self.lines = self.queue.pop(0)
    
    def is_active(self):
        return len(self.lines) and not self.done
    
    def update(self, delta):
        if self.is_active():
            return
        
        self.timer += delta

        if self.timer > 0.1:
            self.timer -= 0.1

            self.current_char += 1

            if self.current_char == len(self.lines[self.current_line]):
                self.current_line += 1

                if self.current_line > len(self.lines) - 1:
                    self.current_line = len(self.lines) - 1
                    self.done = True
                    return
                
                self.current_char = 0
            elif self.lines[self.current_line][self.current_char] != " ":
                speaking_sounds[random.randint(0, len(speaking_sounds) - 1)].play()

    def draw(self, win):
        if len(self.lines):
            pygame.draw.rect(
                win,
                SLOT_BACKGROUND,
                pygame.Rect(WIDTH // 2 - 300, 20, 600, 120),
                border_radius=ITEM_SLOT_BORDER_RADIUS
            )

            y = 25

            for i, line in enumerate(self.lines):
                if i <= self.current_line:
                    if i == 0:
                        t = normal_font_render(line if i != self.current_line else line[:self.current_char], 'white')
                    else:
                        t = small_font_render(line if i != self.current_line else line[:self.current_char], 'white')

                    win.blit(t, (16 + WIDTH // 2 - 295, 16 + y))
                    
                    y += t.get_height() + 5