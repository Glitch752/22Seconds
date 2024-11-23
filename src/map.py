import pygame
from constants import TILE_SIZE, WIDTH, HEIGHT
import random
import time
import os

MAP_WIDTH = 50
MAP_HEIGHT = 25

MAP_UPDATE_RATE = 100
RANDOM_TICK_PER_UPDATE_RATIO = 0.05
last_update = 0

class TILE_TYPE:
    GRASS = 0
    SOIL = 1
    TILLED_SOIL = 2

RANDOM_TICK_TRANSITIONS = {}
RANDOM_TICK_TRANSITIONS[TILE_TYPE.SOIL] = TILE_TYPE.TILLED_SOIL

TILE_IMAGES = {}
def add_tile_image(tile, path):
    TILE_IMAGES[tile] = pygame.image.load(os.path.join("assets", "sprites", path))
add_tile_image(TILE_TYPE.GRASS, "grass.png")
add_tile_image(TILE_TYPE.SOIL, "soil.png")
add_tile_image(TILE_TYPE.TILLED_SOIL, "soil.png")

class Map:
    def __init__(self):
        self.tiles = []
        for x in range(MAP_WIDTH):
            for y in range(MAP_HEIGHT):
                # TODO: Better generation
                self.tiles.append(random.randint(0, 1))
    
    def update(self, delta):
        current_time = time.time()
        if last_update - current_time < MAP_UPDATE_RATE:
            return
        last_update = current_time

        random_ticks = MAP_WIDTH * MAP_HEIGHT * RANDOM_TICK_PER_UPDATE_RATIO
        for i in range(random_ticks):
            tile = random.randint(0, len(self.tiles))
            tile_type = self.tiles[tile]
            if tile_type in RANDOM_TICK_TRANSITIONS:
                self.tiles[tile] = RANDOM_TICK_TRANSITIONS[tile_type]

    def draw(self, win, player):
        for tile_x in range(MAP_WIDTH):
            for tile_y in range(MAP_HEIGHT):
                tile_index = tile_x * MAP_HEIGHT + tile_y
                x = tile_x * TILE_SIZE - player.pos.x + WIDTH // 2
                y = tile_y * TILE_SIZE - player.pos.y + HEIGHT // 2
                tile_type = self.tiles[tile_index]
                image = pygame.transform.scale(TILE_IMAGES[tile_type], (TILE_SIZE, TILE_SIZE))
                win.blit(image, (x, y))