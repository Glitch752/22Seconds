import pygame
from constants import *
from graphics import *

class DialogueManager:
    def __init__(self) -> None:
        self.queue = []
        self.lines = []
    
    def QueueDialogue(self, lines):
        self.queue.append(lines)
    
    def OnConfirm(self):
        self.lines.clear()
        self.lines = self.queue.pop(0)
    
    def Draw(self, win):
        if len(self.lines):
            pygame.draw.rect(win, 'blue', (WIDTH // 2 - 300, HEIGHT // 2 - 150, 600, 300), border_radius=8)
            pygame.draw.rect(win, 'white', (WIDTH // 2 - 300, HEIGHT // 2 - 150, 600, 300), 1, border_radius=8)

            y = HEIGHT // 2 - 145

            for i, line in enumerate(self.lines):
                if i == 0:
                    t = normal_font_render(line, 'white')
                else:
                    t = small_font_render(line, 'white')

                win.blit(t, (WIDTH // 2 - 295, y))
                
                y += t.get_height()