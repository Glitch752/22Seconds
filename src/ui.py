from constants import *
from graphics import *

class Button:
    def __init__(self, text, x, y, pointer, args=()):
        self.text = text

        self.args = args

        w, h = (s := small_font_render(self.text, 'white')).get_width() + 8, s.get_height() + 8

        x -= w // 2
        y -= h // 2

        self.rect = pygame.Rect(x, y, w, h)
        self.pointer = pointer
    
        self.hover = False

        self.normal_color = '#808080'
        self.hover_color = '#c0c0c0'

        self.color = self.normal_color

    def on_hover(self, mx, my):
        c = self.rect.collidepoint(mx, my)
        self.color = self.hover_color if c else self.normal_color
        
        if c and not self.hover:
            # AUDIO['select'].play()
            # TODO Play button hover sound
            pass
        
        self.hover = c

    def on_click(self, mx, my):
        if self.rect.collidepoint(mx, my):
            if self.pointer(*self.args):
                self._timer = self.time_between

    def draw(self, win):
        pygame.draw.rect(win, self.color, self.rect, border_radius=4)

        win.blit(t := SMALL_FONT.render(self.text, False, 'white'), (self.rect.centerx - t.get_width() // 2, self.rect.centery - t.get_height() // 2))
