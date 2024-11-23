import pygame
from constants import WIDTH, HEIGHT

class Player:
    def __init__(self, x, y, r=16):
        self.pos = pygame.Vector2(x, y)
        self.radius = r
        self.speed = 800 # Pixels per second
    
    def update(self, mx, my, delta):
        move = pygame.Vector2(mx, my)

        if move.magnitude():
            move = move.normalize()

        move *= self.speed * delta
        self.pos += move

    def draw(self, win):
        pygame.draw.circle(win, 'red', (WIDTH // 2, HEIGHT // 2), self.radius)