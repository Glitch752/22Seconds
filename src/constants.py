import pygame

# Positive x is right, positive y is down
# Tile grid is based on top left of tiles

GAMENAME = "Funny Farming Game"
WIDTH, HEIGHT = 1280//2, 720//2
TILE_SIZE = 80

DAY_LENGTH = 60 * 2 # Seconds
NIGHT_LENGTH = 22 # Seconds

def lerp(a, b, t):
    return a + (b - a) * t

def clamp(x, mi, ma):
    return max(mi, min(x, ma))