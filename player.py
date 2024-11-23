from constants import *

class Player:
    def __init__(self, x, y, r=16):
        self.pos = pygame.Vector2(x, y)
        self.radius = r
    
    def update(self, mx, my, delta):
        move = pygame.Vector2(mx, my)

        if move.magnitude():
            move = move.normalize()

        move *= self.speed * delta

        pos += move

    def draw(self, win):
        pygame.draw.circle(win, 'red', self.pos, self.radius)