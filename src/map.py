import pygame
from constants import TILE_SIZE, WIDTH, HEIGHT
from graphics import WHITE_IMAGE
import random
import os
import math

MAP_WIDTH = 25
MAP_HEIGHT = 10

MAP_UPDATE_RATE = 600
RANDOM_TICK_PER_UPDATE_RATIO = 0.01
last_update = 0

class TILE_TYPE:
    GRASS = 0
    SOIL = 1
    TILLED_SOIL = 2

RANDOM_TICK_TRANSITIONS = {}
RANDOM_TICK_TRANSITIONS[TILE_TYPE.SOIL] = TILE_TYPE.TILLED_SOIL

TILE_IMAGES = {}
def add_tile_image(tile, path):
    original_image = pygame.image.load(os.path.join("assets", "sprites", path))
    image = pygame.transform.scale(original_image, (TILE_SIZE, TILE_SIZE))
    TILE_IMAGES[tile] = image

add_tile_image(TILE_TYPE.GRASS, "grass.png")
add_tile_image(TILE_TYPE.SOIL, "soil.png")
add_tile_image(TILE_TYPE.TILLED_SOIL, "tilled_soil.png")

class Map:
    def __init__(self):
        self.tiles = []
        for x in range(MAP_WIDTH):
            for y in range(MAP_HEIGHT):
                # TODO: Better generation
                self.tiles.append(random.randint(0, 1))
    
    def update(self, delta):
        global last_update
        current_time = pygame.time.get_ticks()
        if current_time - last_update < MAP_UPDATE_RATE:
            return
        last_update = current_time

        random_ticks = math.ceil(MAP_WIDTH * MAP_HEIGHT * RANDOM_TICK_PER_UPDATE_RATIO)
        for i in range(random_ticks):
            tile = random.randint(0, len(self.tiles) - 1)
            
            tile_type = self.tiles[tile]
            if tile_type in RANDOM_TICK_TRANSITIONS:
                self.tiles[tile] = RANDOM_TICK_TRANSITIONS[tile_type]

    def draw(self, win, player, sx, sy):
        for tile_x in range(MAP_WIDTH):
            for tile_y in range(MAP_HEIGHT):
                tile_index = tile_x * MAP_HEIGHT + tile_y
                x = tile_x * TILE_SIZE - player.pos.x + WIDTH // 2
                y = tile_y * TILE_SIZE - player.pos.y + HEIGHT // 2
                tile_type = self.tiles[tile_index]
                win.blit(TILE_IMAGES[tile_type], (x, y))

        # draw outline
        x = sx * TILE_SIZE - player.pos.x + WIDTH // 2
        y = sy * TILE_SIZE - player.pos.y + HEIGHT // 2
        win.blit(WHITE_IMAGE, (x, y))
        pygame.draw.rect(win, 'yellow', (x, y, TILE_SIZE, TILE_SIZE), 1)