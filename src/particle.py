import pygame
import random
from graphics import WIDTH, HEIGHT

class Particle:
    def __init__(self, x, y, color):
        self.pos = pygame.Vector2(x, y)
        self.color = color
        self.lifetime = 1 + random.random() * 0.5
        self.angle = random.random() * 360
        self.rot_speed = random.randint(-720, 720)
        self.speed = random.randint(35, 70)
        self.size = random.randint(2, 5)
        self.timer = 0
        self.done = False

    def draw(self, win, offset):
        s = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        s.fill(self.color)
        s.set_alpha(255 * (1 - (self.timer / self.lifetime)))
        s = pygame.transform.rotate(s, self.angle)

        p = self.pos + pygame.Vector2(WIDTH//2, HEIGHT//2) - offset

        win.blit(s, p)
    
    def update(self, delta):
        self.timer += delta
        if self.timer >= self.lifetime:
            self.done = True
        self.angle += self.rot_speed * delta
        self.pos.y -= self.speed * delta

particles: list[Particle] = []

def draw_particles(win, camera_pos):
    global particles
    for p in particles:
        p.draw(win, camera_pos)

def update_particles(delta):
    global particles
    
    i = 0
    while i < len(particles):
        particle = particles[i]
        particle.update(delta)

        if particle.done:
            particles.pop(i)
            i -= 1
        i += 1

def spawn_particles_in_square(x, y, color, radius=5, num=1):
    global particles
    import random
    particles += [
        Particle(x + random.randint(-radius, radius), y + random.randint(-radius, radius), color) for _ in range(num)
    ]