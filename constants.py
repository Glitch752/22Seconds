import pygame

pygame.init()

BIG_FONT = pygame.font.SysFont("Consolas", 36)
FONT = pygame.font.SysFont("Consolas", 30)
SMALL_FONT = pygame.font.SysFont("Consolas", 24)

GAMENAME = "Funny Farming Game"

WIDTH, HEIGHT = 1280, 720

WIN = pygame.display.set_mode((WIDTH, HEIGHT))

TILE_SIZE = 64

def lerp(a, b, t):
    return a + (b - a) * t

def clamp(x, mi, ma):
    return max(mi, min(x, ma))