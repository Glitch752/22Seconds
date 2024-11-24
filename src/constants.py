import pygame

# Positive x is right, positive y is down
# Tile grid is based on top left of tiles

GAMENAME = "22 Seconds"
WIDTH, HEIGHT = 1280, 720
TILE_SIZE = 80

DAY_LENGTH = 120 # Seconds
DUSK_DAWN_LENGTH = 10 # Seconds
NIGHT_LENGTH = 22 # Seconds

def lerp(a, b, t):
    return a + (b - a) * t

def clamp(x, mi, ma):
    return max(mi, min(x, ma))