import pygame
import pygame.midi
from constants import TILE_SIZE, WIDTH, HEIGHT
from particle import spawn_particles_in_square
from graphics import WHITE_IMAGE, add_floating_text_hint, FloatingHintText
from items import ITEM_NAMES, ITEM_TYPE
import random
import os
import math

MAP_WIDTH = 50
MAP_HEIGHT = 30

MAP_UPDATE_RATE = 600
PARTICLES_PER_TILE_SECOND = 5
RANDOM_TICK_PER_UPDATE_RATIO = 0.01
last_map_update = 0
last_particle_spawn = 0

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
    WALL = 12
    DESTROYED_WALL = 13

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
        original_image = pygame.image.load(os.path.join("assets", "tiles", path)).convert()
    except Exception as e:
        original_image = pygame.image.load(os.path.join("assets", "sprites", "unknown.png")).convert() # TEMPORARY
    image = pygame.transform.scale(original_image, (TILE_SIZE, TILE_SIZE))
    TILE_IMAGES[tile] = image

add_tile_image(TILE_TYPE.GRASS, "short_grass.png")
add_tile_image(TILE_TYPE.SOIL, "dirt.png")
add_tile_image(TILE_TYPE.TILLED_SOIL, "farmland.png")
add_tile_image(TILE_TYPE.PLANTED_CARROT_0, "planted_carrot_0.png")
add_tile_image(TILE_TYPE.PLANTED_CARROT_1, "planted_carrot_1.png")
add_tile_image(TILE_TYPE.PLANTED_CARROT_2, "planted_carrot_2.png")
add_tile_image(TILE_TYPE.PLANTED_WHEAT_0, "planted_wheat_0.png")
add_tile_image(TILE_TYPE.PLANTED_WHEAT_1, "planted_wheat_1.png")
add_tile_image(TILE_TYPE.PLANTED_WHEAT_2, "planted_wheat_2.png")
add_tile_image(TILE_TYPE.PLANTED_ONION_0, "planted_onion_0.png")
add_tile_image(TILE_TYPE.PLANTED_ONION_1, "planted_onion_1.png")
add_tile_image(TILE_TYPE.PLANTED_ONION_2, "planted_onion_2.png")
add_tile_image(TILE_TYPE.WALL, "wall.png")
add_tile_image(TILE_TYPE.DESTROYED_WALL, "destroyed_wall.png")

SEED_ITEM_TO_TILE = {}
SEED_ITEM_TO_TILE[ITEM_TYPE.CARROT_SEEDS] = TILE_TYPE.PLANTED_CARROT_0
SEED_ITEM_TO_TILE[ITEM_TYPE.WHEAT_SEEDS] = TILE_TYPE.PLANTED_WHEAT_0
SEED_ITEM_TO_TILE[ITEM_TYPE.ONION_SEEDS] = TILE_TYPE.PLANTED_ONION_0

TILE_PARTICLES = {}
TILE_PARTICLES[TILE_TYPE.PLANTED_CARROT_2] = "orange"
TILE_PARTICLES[TILE_TYPE.PLANTED_WHEAT_2] = "yellow"
TILE_PARTICLES[TILE_TYPE.PLANTED_ONION_2] = "purple"

COLLISION_TILES = set([TILE_TYPE.WALL])

tilling_sound = pygame.mixer.Sound(os.path.join("assets", "audio", "till.wav"))
harvesting_sound = pygame.mixer.Sound(os.path.join("assets", "audio", "pickUp.wav"))
planting_sound = pygame.mixer.Sound(os.path.join("assets", "audio", "plant.wav"))

class Map:
    def __init__(self):
        self.tiles = []
        for x in range(MAP_WIDTH):
            for y in range(MAP_HEIGHT):
                # TODO: Better generation
                self.tiles.append(TILE_TYPE.SOIL)
    
    def update(self):
        global last_map_update
        current_time = pygame.time.get_ticks()
        if current_time - last_map_update < MAP_UPDATE_RATE:
            return
        last_map_update = current_time

        random_ticks = math.ceil(MAP_WIDTH * MAP_HEIGHT * RANDOM_TICK_PER_UPDATE_RATIO)
        for i in range(random_ticks):
            tile = random.randint(0, len(self.tiles) - 1)
            
            tx, ty = tile % MAP_WIDTH, tile // MAP_WIDTH

            tile_type = self.tiles[tile]
            if tile_type in RANDOM_TICK_TRANSITIONS:
                self.tiles[tile] = RANDOM_TICK_TRANSITIONS[tile_type]
    
    def is_collision(self, tile_x, tile_y):
        tile_index = int(tile_x * MAP_HEIGHT + tile_y)
        if tile_index < 0 or tile_index >= len(self.tiles):
            return False
        return self.tiles[tile_index] in COLLISION_TILES
     
    def tilled(self, tile_index, tile_center_pos):
        self.tiles[tile_index] = TILE_TYPE.TILLED_SOIL
        tilling_sound.play()
        add_floating_text_hint(FloatingHintText(f"Tilled soil!", tile_center_pos, "white"))
    
    def harvested(self, tile_index, tile_center_pos, player):
        item = self.tiles[tile_index]
        self.tiles[tile_index] = TILE_TYPE.TILLED_SOIL
        harvesting_sound.play()
        item_type = None
        if item == TILE_TYPE.PLANTED_CARROT_2:
            i = 0
            item_type = ITEM_TYPE.CARROT
        elif item == TILE_TYPE.PLANTED_ONION_2:
            i = 1
            item_type = ITEM_TYPE.ONION
        elif item == TILE_TYPE.PLANTED_WHEAT_2:
            i = 2
            item_type = ITEM_TYPE.WHEAT
        else:
            i = 3
        r = random.randint(1, 2)
        add_floating_text_hint(FloatingHintText(f"+{r} {['Carrot', 'Onion', 'Wheat', 'ERROR'][i]}", tile_center_pos, "green"))
        player.items[item_type] += r
    def planted(self, tile_index, tile_center_pos, item):
        self.tiles[tile_index] = SEED_ITEM_TO_TILE[item]
        planting_sound.play()
        add_floating_text_hint(FloatingHintText(f"-1 {ITEM_NAMES[item]}", tile_center_pos, "orange"))
        return -1
    def wall_placed(self, tile_index, tile_center_pos):
        self.tiles[tile_index] = TILE_TYPE.WALL
        planting_sound.play() # TODO: THUNK sound
        add_floating_text_hint(FloatingHintText(f"Placed wall!", tile_center_pos, "white"))
        return -1
    def broken(self, tile_index, tile_center_pos):
        self.tiles[tile_index] = TILE_TYPE.DESTROYED_WALL
        planting_sound.play() # TODO: CHOP sound
        add_floating_text_hint(FloatingHintText(f"Broke wall!", tile_center_pos, "red"))
    
    def get_interaction(self, tile_x, tile_y, item, player):
        """
        Returns a lambda that will execute the proper interaction based on the selected tile and item,
        or None if no interaction should occur.
        The lambda will return -1 if the selected item's quantity should be decremented.
        """
        tile_index = tile_x * MAP_HEIGHT + tile_y
        if tile_index < 0 or tile_index >= len(self.tiles):
            return

        tile_center_pos = (
            tile_x * TILE_SIZE + TILE_SIZE // 2 + WIDTH // 2,
            tile_y * TILE_SIZE + TILE_SIZE // 2 + HEIGHT // 2 - TILE_SIZE
        )
        tile_type = self.tiles[tile_index]
        match item:
            case ITEM_TYPE.HOE:
                if tile_type == TILE_TYPE.SOIL:
                    return (lambda: self.tilled(tile_index, tile_center_pos))
                elif tile_type in [TILE_TYPE.PLANTED_CARROT_2, TILE_TYPE.PLANTED_ONION_2, TILE_TYPE.PLANTED_WHEAT_2]:
                    return (lambda: self.harvested(tile_index, tile_center_pos, player))
                else:
                    return None
            case ITEM_TYPE.AXE:
                if tile_type == TILE_TYPE.WALL:
                    return (lambda: self.broken(tile_index, tile_center_pos))
            case ITEM_TYPE.WALL:
                if pygame.Rect(tile_x * TILE_SIZE, tile_y * TILE_SIZE, TILE_SIZE, TILE_SIZE)\
                    .colliderect(player.pos.x - player.radius, player.pos.y - player.radius, player.radius*2, player.radius*2):
                    return None
                if tile_type == TILE_TYPE.SOIL:
                    return (lambda: self.wall_placed(tile_index, tile_center_pos))
            case ITEM_TYPE.CARROT_SEEDS | ITEM_TYPE.WHEAT_SEEDS | ITEM_TYPE.ONION_SEEDS:
                if tile_type != TILE_TYPE.TILLED_SOIL:
                    return None
                return (lambda: self.planted(tile_index, tile_center_pos, item)) if item in SEED_ITEM_TO_TILE else None

    def draw(self, win: pygame.Surface, delta, player, outline_x, outline_y, outline_color):
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
                    if random.random() < delta * PARTICLES_PER_TILE_SECOND and tile_type in TILE_PARTICLES:
                        spawn_particles_in_square(tile_x * TILE_SIZE + TILE_SIZE//2, tile_y * TILE_SIZE + TILE_SIZE//2, TILE_PARTICLES[tile_type], TILE_SIZE//2, 1)
                else:
                    tile_type = TILE_TYPE.SOIL
                blits.append([TILE_IMAGES[tile_type], (x, y)])
        win.blits(blits, False)

        # Draw outline
        x = outline_x * TILE_SIZE - player.pos.x + WIDTH // 2
        y = outline_y * TILE_SIZE - player.pos.y + HEIGHT // 2
        win.blit(WHITE_IMAGE, (x, y))
        pygame.draw.rect(win, outline_color, (x, y, TILE_SIZE, TILE_SIZE), 1)