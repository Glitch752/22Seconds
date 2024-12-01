from perlin_noise import PerlinNoise
import pygame
from audio import AudioManager
from constants import FARMABLE_MAP_END, FARMABLE_MAP_START, INTERACTABLE_SELECTION_COLOR, NON_INTERACTABLE_SELECTION_COLOR, NOTHING_SELECTION_COLOR, TILE_SIZE
import random
import math
from constants import MAP_WIDTH, MAP_HEIGHT, MAP_UPDATE_RATE, RANDOM_TICK_PER_UPDATE_RATIO
from typing import TYPE_CHECKING, Callable
from dialogue import DialogueManager
from graphics import get_height, get_width
from items import Item
from map.entity import Entity
from map.tile import Tile, TileType
from utils import get_asset

if TYPE_CHECKING:
    from player import Player

class Map:
    last_map_update: float = 0
    tiles: list[Tile]
    entities: list[Entity]
    
    selection_images: dict[str, pygame.Surface] = {}
    
    def __init__(self):
        self.tiles = []
        
        for color in [NON_INTERACTABLE_SELECTION_COLOR, INTERACTABLE_SELECTION_COLOR, NOTHING_SELECTION_COLOR]:
            for variant in ["0", "1"]:
                image = pygame.image.load(get_asset("ui", f"selector_{color}_{variant}.png")).convert_alpha()
                image = pygame.transform.scale(image, (TILE_SIZE, TILE_SIZE * 17 // 16))
                self.selection_images[f"{color}_{variant}"] = image
        
        noise = PerlinNoise(octaves=4, seed=100)
        max_dim = max(MAP_WIDTH, MAP_HEIGHT)
        for x in range(MAP_WIDTH):
            for y in range(MAP_HEIGHT):
                if x >= FARMABLE_MAP_START[0] and x < FARMABLE_MAP_END[0] and y >= FARMABLE_MAP_START[1] and y < FARMABLE_MAP_END[1]:
                    val = noise.noise([x / max_dim, y / max_dim])
                    self.tiles.append(Tile(TileType.GRASS if val > 0 else TileType.TALL_GRASS))
                else:
                    self.tiles.append(Tile(TileType.OUTSIDE_FARM_DIRT))

        WATER_POOL_START = (MAP_WIDTH // 4 - 2, MAP_HEIGHT // 2 - 2)
        WATER_POOL_END = (MAP_WIDTH // 4 + 2, MAP_HEIGHT // 2 + 2)
        for x in range(WATER_POOL_START[0], WATER_POOL_END[0]):
            for y in range(WATER_POOL_START[1], WATER_POOL_END[1]):
                self.tiles[x * MAP_HEIGHT + y] = Tile(TileType.WATER)
        
        self.entities = []
    
    def add_entity(self, entity: Entity):
        self.entities.append(entity)
    
    def update(self, audio_manager: AudioManager, dialogue_manager: DialogueManager):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_map_update < MAP_UPDATE_RATE:
            return
        self.last_map_update = current_time

        random_ticks = math.ceil(MAP_WIDTH * MAP_HEIGHT * RANDOM_TICK_PER_UPDATE_RATIO)
        for i in range(random_ticks):
            tile = random.randint(0, len(self.tiles) - 1)
            self.tiles[tile].random_tick(audio_manager, dialogue_manager)
    
    def is_collision(self, tile_x, tile_y):
        tile_index = int(tile_x * MAP_HEIGHT + tile_y)
        if tile_index < 0 or tile_index >= len(self.tiles):
            return False
        return self.tiles[tile_index].is_collidable()
    
    def get_interaction(self, tile_x: int, tile_y: int, item: Item, player: "Player", audio_manager: AudioManager, dialogue_manager: DialogueManager, rising_edge: bool) -> Callable[[], None]:
        """
        Returns a lambda that will execute the proper interaction based on the selected tile and item,
        or None if no interaction should occur.
        """
        tile_index = tile_x * MAP_HEIGHT + tile_y
        if tile_index < 0 or tile_index >= len(self.tiles):
            return
        
        if rising_edge:
            for entity in self.entities:
                interaction = entity.get_interaction(tile_x, tile_y)
                if interaction:
                    return interaction

        tile_center_pos = (tile_x * TILE_SIZE + TILE_SIZE // 2, tile_y * TILE_SIZE + TILE_SIZE // 2)
        return self.tiles[tile_index].get_interaction(item, player, audio_manager, dialogue_manager, tile_center_pos, rising_edge)

    def check_proximity_interaction(self, player: "Player") -> Callable[[], None]:
        for entity in self.entities:
            interaction = entity.check_proximity_interaction(player)
            if interaction:
                return interaction
        return None

    last_draw_time = 0
    def draw(self, win: pygame.Surface, camera_position: pygame.Vector2, player: "Player", selected_cell_x: int, selected_cell_y: int, selection_color: str, clicking: bool, interacting: bool):
        current_time = pygame.time.get_ticks()
        delta = (current_time - self.last_draw_time) / 1000
        self.last_draw_time = current_time
        
        x_start = math.floor((camera_position.x - get_width() / 2) / TILE_SIZE) - 1
        x_end = math.ceil((camera_position.x + get_width() / 2) / TILE_SIZE)
        y_start = math.floor((camera_position.y - get_height() / 2) / TILE_SIZE) - 1
        y_end = math.ceil((camera_position.y + get_height() / 2) / TILE_SIZE)
        
        tile_positions = [(
            x * TILE_SIZE - camera_position.x + get_width() // 2,
            y * TILE_SIZE - camera_position.y + get_height() // 2,
            x, y
        ) for x in range(x_start, x_end) for y in range(y_start, y_end)]
        
        # Draw the main tile grid
        blit_layers: list[list[tuple[pygame.Surface, tuple[int, int]]]] = [[] for _ in range(len(TileType))]
        blank_tile = Tile(TileType.SOIL)
        for (x, y, tile_x, tile_y) in tile_positions:
            # Since this is a dual-grid system, we perform the following steps:
            # - Get the tile at each corner of the drawn tile position
            # - Separate the tiles into 1-4 bitmasks--one per type of tile
            # - Look up the bitmask with its tile type in tilemap_atlases, BUT draw the lowest layer as a full tile
            # - Add the resulting image to the blit_layers list based on the layer of the tile type
            
            # Get the tile at each corner of the drawn tile position
            corner_tiles = [
                (tile_x, tile_y),
                (tile_x + 1, tile_y),
                (tile_x, tile_y + 1),
                (tile_x + 1, tile_y + 1)
            ]
            corner_tiles = list(map(
                lambda pos: self.tiles[pos[0] * MAP_HEIGHT + pos[1]] if pos[0] >= 0 and pos[0] < MAP_WIDTH and pos[1] >= 0 and pos[1] < MAP_HEIGHT else blank_tile,
                corner_tiles
            ))
            
            # Separate the tiles into a bitmask per tile type
            bitmasks: dict[TileType, int] = {}
            for (tile, i) in zip(corner_tiles, range(4)):
                if tile.tile_type not in bitmasks:
                    bitmasks[tile.tile_type] = 0
                bitmasks[tile.tile_type] |= 1 << i
            
            lowest_layer = min(map(lambda tile: tile.layer, bitmasks))

            # Draw the tile based on the bitmask
            dual_grid_pos = (x + TILE_SIZE // 2, y + TILE_SIZE // 2)
            for tile_type, bitmask in bitmasks.items():
                if tile_type.layer == lowest_layer:
                    bitmask = 0b1111
                
                atlas: pygame.Surface = tile_type.atlas[bitmask]
                blit_layers[tile_type.layer].append((atlas, dual_grid_pos))
        
        for blits in blit_layers:
            if len(blits) == 0:
                continue
            win.blits(blits, False)
        
        # Draw everything on tiles
        for (x, y, tile_x, tile_y) in filter(lambda pos: pos != None, tile_positions):
            idx = tile_x * MAP_HEIGHT + tile_y
            if idx >= 0 and idx < len(self.tiles):
                tile_center_pos = (tile_x * TILE_SIZE + TILE_SIZE // 2, tile_y * TILE_SIZE + TILE_SIZE // 2)
                self.tiles[idx].draw(win, x, y, tile_center_pos, delta)
        
        # Draw entities
        for entity in self.entities:
            entity.draw(win, camera_position, player, self.selection_images["green_1"] if interacting else self.selection_images["green_0"])
        
        # Draw selection
        x = selected_cell_x * TILE_SIZE - camera_position.x + get_width() // 2
        y = selected_cell_y * TILE_SIZE - camera_position.y + get_height() // 2
        win.blit(self.selection_images[selection_color + "_" + ("1" if clicking else "0")], (x, y))