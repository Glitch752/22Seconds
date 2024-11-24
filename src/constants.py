import pygame

# Positive x is right, positive y is down
# Tile grid is based on top left of tiles

GAMENAME = "Funny Farming Game"
WIDTH, HEIGHT = 1280, 720
TILE_SIZE = 80

DAY_LENGTH = 8 # Seconds
DUSK_DAWN_LENGTH = 3 # Seconds
NIGHT_LENGTH = 3 # Seconds

def lerp(a, b, t):
    return a + (b - a) * t

def clamp(x, mi, ma):
    return max(mi, min(x, ma))

def spawn_particles_in_square(x, y, color, radius=5, num=20):
    from particle import Particle
    import random
    return [
        Particle(x + random.randint(-radius, radius), y + random.randint(-radius, radius), color) for _ in range(num)
    ]