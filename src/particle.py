import pygame
import random
from graphics import WIDTH, HEIGHT

class Particle:
    def __init__(self, x, y, color):
        self.pos = pygame.Vector2(x, y)
        self.color = color
        self.lifetime = 1 + random.random() * 0.5
        self.angle = 0
        self.rot_speed = 10 + random.randint(0, 5)
        self.speed = random.randint(50, 200)
        self.size = random.randint(2, 4)
        self.timer = 0
        self.done = False

    def draw(self, win, offset):
        s = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        s.fill(self.color)
        s.set_alpha(255 * (1 - (self.timer / self.lifetime)))
    
        p = self.pos + pygame.Vector2(WIDTH, HEIGHT) - offset
        print(p)

        win.blit(s, p)
    
    def update(self, delta):
        self.timer += delta
        if self.timer >= self.lifetime:
            self.done = True
        self.angle += self.rot_speed * delta
        self.pos.y -= self.speed * delta