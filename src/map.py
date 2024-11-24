import pygame
from constants import TILE_SIZE, WIDTH, HEIGHT
from graphics import WHITE_IMAGE
from items import ITEM_TYPE
import random
import os
import math

MAP_WIDTH = 50
MAP_HEIGHT = 30

MAP_UPDATE_RATE = 600
RANDOM_TICK_PER_UPDATE_RATIO = 0.01
last_update = 0

class TILE_TYPE:
    GRASS = 0
    SOIL = 1
    TILLED_SOIL = 2
    PLANTED_CARROT_0 = 3
    PLANTED_CARROT_1 = 4
    PLANTED_CARROT_2 = 5
    PLANTED_WHEAT_0 = 6
    PLANTED_WHEAT_1 = 7
    PLANTED_WHEAT_2 = 8
    PLANTED_ONION_0 = 9
    PLANTED_ONION_1 = 10
    PLANTED_ONION_2 = 11

RANDOM_TICK_TRANSITIONS = {}
RANDOM_TICK_TRANSITIONS[TILE_TYPE.PLANTED_CARROT_0] = TILE_TYPE.PLANTED_CARROT_1
RANDOM_TICK_TRANSITIONS[TILE_TYPE.PLANTED_CARROT_1] = TILE_TYPE.PLANTED_CARROT_2
RANDOM_TICK_TRANSITIONS[TILE_TYPE.PLANTED_WHEAT_0] = TILE_TYPE.PLANTED_WHEAT_1
RANDOM_TICK_TRANSITIONS[TILE_TYPE.PLANTED_WHEAT_1] = TILE_TYPE.PLANTED_WHEAT_2
RANDOM_TICK_TRANSITIONS[TILE_TYPE.PLANTED_ONION_0] = TILE_TYPE.PLANTED_ONION_1
RANDOM_TICK_TRANSITIONS[TILE_TYPE.PLANTED_ONION_1] = TILE_TYPE.PLANTED_ONION_2

TILE_IMAGES = {}
def add_tile_image(tile, path):
    try:
        original_image = pygame.image.load(os.path.join("assets", "sprites", path))
    except Exception as e:
        original_image = pygame.image.load(os.path.join("assets", "sprites", "unknown.png")) # TEMPORARY
    image = pygame.transform.scale(original_image, (TILE_SIZE, TILE_SIZE))
    TILE_IMAGES[tile] = image

add_tile_image(TILE_TYPE.GRASS, "grass.png")
add_tile_image(TILE_TYPE.SOIL, "soil.png")
add_tile_image(TILE_TYPE.TILLED_SOIL, "tilled_soil.png")
add_tile_image(TILE_TYPE.PLANTED_CARROT_0, "planted_carrot_0.png")
add_tile_image(TILE_TYPE.PLANTED_CARROT_1, "planted_carrot_1.png")
add_tile_image(TILE_TYPE.PLANTED_CARROT_2, "planted_carrot_2.png")
add_tile_image(TILE_TYPE.PLANTED_WHEAT_0, "planted_wheat_0.png")
add_tile_image(TILE_TYPE.PLANTED_WHEAT_1, "planted_wheat_1.png")
add_tile_image(TILE_TYPE.PLANTED_WHEAT_2, "planted_wheat_2.png")
add_tile_image(TILE_TYPE.PLANTED_ONION_0, "planted_onion_0.png")
add_tile_image(TILE_TYPE.PLANTED_ONION_1, "planted_onion_1.png")
add_tile_image(TILE_TYPE.PLANTED_ONION_2, "planted_onion_2.png")

SEED_ITEM_TO_TILE = {}
SEED_ITEM_TO_TILE[ITEM_TYPE.CARROT_SEEDS] = TILE_TYPE.PLANTED_CARROT_0
SEED_ITEM_TO_TILE[ITEM_TYPE.WHEAT_SEEDS] = TILE_TYPE.PLANTED_WHEAT_0
SEED_ITEM_TO_TILE[ITEM_TYPE.ONION_SEEDS] = TILE_TYPE.PLANTED_ONION_0

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
    
    def tilled(self, tile_index):
        self.tiles[tile_index] = TILE_TYPE.TILLED_SOIL
        # TODO: Tilling sound effect
    def planted(self, tile_index, item):
        self.tiles[tile_index] = SEED_ITEM_TO_TILE[item]
        return -1
        # TODO: Planting sound effect
    
    def get_interaction(self, tile_x, tile_y, item):
        """
        Returns a lambda that will execute the proper interaction based on the selected tile and item,
        or None if no interaction should occur.
        The lambda will return -1 if the selected item's quantity should be decremented.
        """
        tile_index = tile_x * MAP_HEIGHT + tile_y
        if tile_index < 0 or tile_index >= len(self.tiles):
            return

        tile_type = self.tiles[tile_index]
        match item:
            case ITEM_TYPE.HOE:
                return (lambda: self.tilled(tile_index)) if tile_type == TILE_TYPE.SOIL else None
            case ITEM_TYPE.CARROT_SEEDS | ITEM_TYPE.WHEAT_SEEDS | ITEM_TYPE.ONION_SEEDS:
                if tile_type != TILE_TYPE.TILLED_SOIL:
                    return None
                return (lambda: self.planted(tile_index, item)) if item in SEED_ITEM_TO_TILE else None

    def draw(self, win: pygame.Surface, player, outline_x, outline_y, outline_color):
        x_start = math.floor((player.pos.x - WIDTH / 2) / TILE_SIZE)
        x_end = math.ceil((player.pos.x + WIDTH / 2) / TILE_SIZE)
        y_start = math.floor((player.pos.y - HEIGHT / 2) / TILE_SIZE)
        y_end = math.ceil((player.pos.y + HEIGHT / 2) / TILE_SIZE)
        blits = []
        for tile_x in range(x_start, x_end):
            for tile_y in range(y_start, y_end):
                x = tile_x * TILE_SIZE - player.pos.x + WIDTH // 2
                y = tile_y * TILE_SIZE - player.pos.y + HEIGHT // 2
                if tile_x >= 0 and tile_x < MAP_WIDTH and tile_y >= 0 and tile_y < MAP_HEIGHT:
                    tile_type = self.tiles[tile_x * MAP_HEIGHT + tile_y]
                else:
                    tile_type = TILE_TYPE.SOIL
                blits.append([TILE_IMAGES[tile_type], (x, y)])
        win.blits(blits, False)

        # Draw outline
        x = outline_x * TILE_SIZE - player.pos.x + WIDTH // 2
        y = outline_y * TILE_SIZE - player.pos.y + HEIGHT // 2
        win.blit(WHITE_IMAGE, (x, y))
        # TODO: Different outline color when hovering over something interactable
        pygame.draw.rect(win, outline_color, (x, y, TILE_SIZE, TILE_SIZE), 1)