from perlin_noise import PerlinNoise
import pygame
import pygame.midi
from audio import AudioManager
from constants import TILE_SIZE, WIDTH, HEIGHT
import random
import math
from constants import MAP_WIDTH, MAP_HEIGHT, MAP_UPDATE_RATE, RANDOM_TICK_PER_UPDATE_RATIO
from typing import TYPE_CHECKING
from map.tile import Tile, TileType, tilemap_atlases

if TYPE_CHECKING:
    from player import Player

class Map:
    last_map_update: float = 0
    tiles: list[Tile]
    
    def __init__(self):
        self.tiles = []
        
        noise = PerlinNoise(octaves=4, seed=100)
        max_dim = max(MAP_WIDTH, MAP_HEIGHT)
        for x in range(MAP_WIDTH):
            for y in range(MAP_HEIGHT):
                val = noise.noise([x / max_dim, y / max_dim])
                self.tiles.append(Tile(TileType.GRASS if val > 0 else TileType.TALL_GRASS))
        
        # Add a water pool
        self.tiles[(MAP_WIDTH // 2) * MAP_HEIGHT + 2] = Tile(TileType.WATER)
        self.tiles[(MAP_WIDTH // 2) * MAP_HEIGHT + 3] = Tile(TileType.WATER)
        self.tiles[(MAP_WIDTH // 2 + 1) * MAP_HEIGHT + 2] = Tile(TileType.WATER)
        self.tiles[(MAP_WIDTH // 2 + 1) * MAP_HEIGHT + 3] = Tile(TileType.WATER)
    
    def update(self, audio_manager: AudioManager):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_map_update < MAP_UPDATE_RATE:
            return
        self.last_map_update = current_time

        random_ticks = math.ceil(MAP_WIDTH * MAP_HEIGHT * RANDOM_TICK_PER_UPDATE_RATIO)
        for i in range(random_ticks):
            tile = random.randint(0, len(self.tiles) - 1)
            self.tiles[tile].random_tick(audio_manager)
    
    def is_collision(self, tile_x, tile_y):
        tile_index = int(tile_x * MAP_HEIGHT + tile_y)
        if tile_index < 0 or tile_index >= len(self.tiles):
            return False
        return self.tiles[tile_index].is_collidable()
    
    def get_interaction(self, tile_x, tile_y, item: int, player: "Player", audio_manager: AudioManager):
        """
        Returns a lambda that will execute the proper interaction based on the selected tile and item,
        or None if no interaction should occur.
        """
        tile_index = tile_x * MAP_HEIGHT + tile_y
        if tile_index < 0 or tile_index >= len(self.tiles):
            return

        tile_center_pos = (
            tile_x * TILE_SIZE + TILE_SIZE // 2 + WIDTH // 2,
            tile_y * TILE_SIZE + TILE_SIZE // 2 + HEIGHT // 2
        )
        return self.tiles[tile_index].get_interaction(item, player, audio_manager, tile_center_pos)

    last_draw_time = 0
    def draw(self, win: pygame.Surface, camera_position: pygame.Vector2):
        current_time = pygame.time.get_ticks()
        delta = (current_time - self.last_draw_time) / 1000
        self.last_draw_time = current_time
        
        x_start = math.floor((camera_position.x - WIDTH / 2) / TILE_SIZE) - 1
        x_end = math.ceil((camera_position.x + WIDTH / 2) / TILE_SIZE)
        y_start = math.floor((camera_position.y - HEIGHT / 2) / TILE_SIZE) - 1
        y_end = math.ceil((camera_position.y + HEIGHT / 2) / TILE_SIZE)
        
        tile_positions = [(
            x * TILE_SIZE - camera_position.x + WIDTH // 2,
            y * TILE_SIZE - camera_position.y + HEIGHT // 2,
            x, y
        ) for x in range(x_start, x_end) for y in range(y_start, y_end)]
        
        # Draw the main tile grid
        blit_layers: list[list[tuple[pygame.Surface, tuple[int, int]]]] = [[] for _ in range(TileType.NUM_LAYERS)]
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
            bitmasks = {}
            for (tile, i) in zip(corner_tiles, range(4)):
                if tile.tile_type not in bitmasks:
                    bitmasks[tile.tile_type] = 0
                bitmasks[tile.tile_type] |= 1 << i
            
            bitmask_layers = [(tile_type, bitmask, TileType.get_layer(tile_type)) for (tile_type, bitmask) in bitmasks.items()]
            lowest_layer = min(map(lambda layer: layer[2], bitmask_layers))

            # Draw the tile based on the bitmask
            dual_grid_pos = (x + TILE_SIZE // 2, y + TILE_SIZE // 2)
            for (tile_type, bitmask, layer) in bitmask_layers:
                if layer == lowest_layer:
                    bitmask = 0b1111
                
                atlas: pygame.Surface = tilemap_atlases[tile_type][bitmask]
                blit_layers[layer].append((atlas, dual_grid_pos))
        
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