import pygame
from constants import *
from graphics import *

class DialogueManager:
    def __init__(self) -> None:
        self.queue = []
        self.lines = []
        self.current_char = 0
        self.current_line = 0
        self.timer = 0
        self.done = False

    def QueueDialogue(self, lines):
        self.queue.append(lines)
    
    def OnConfirm(self):
        self.done = False
        self.current_char = 0
        self.current_line = 0
        self.lines.clear()
        if len(self.queue):
            self.lines = self.queue.pop(0)
    
    def Update(self, delta):
        if self.done or not len(self.lines):
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

    def Draw(self, win):
        if len(self.lines):
            draw_patchrect(win, pygame.Rect(WIDTH // 2 - 300, HEIGHT * 0.9 - 75, 600, 150))

            y = HEIGHT * 0.9 - 70

            for i, line in enumerate(self.lines):
                if i <= self.current_line:
                    if i == 0:
                        t = normal_font_render(line if i != self.current_line else line[:self.current_char], 'white')
                    else:
                        t = small_font_render(line if i != self.current_line else line[:self.current_char], 'white')

                    win.blit(t, (16 + WIDTH // 2 - 295, 16 + y))
                    
                    y += t.get_height() + 5