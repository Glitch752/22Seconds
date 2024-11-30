import pygame
from typing import TYPE_CHECKING, Callable, Optional
import os

from constants import MAP_HEIGHT, MAP_WIDTH, TILE_SIZE
from graphics import get_height, get_width

if TYPE_CHECKING:
    from player import Player
    from map import Map


class Feature:
    """A feature is an image placed in the world that can be interacted with."""
    tile_x: int
    tile_y: int
    tile_width: int
    tile_height: int
    
    image: pygame.Surface
    interaction: Optional[Callable[[], None]]
    
    def __init__(self, tile_x: int, tile_y: int, tile_width: int, tile_height: int, path: str, interaction: Optional[Callable[[], None]] = None):
        self.tile_x = tile_x
        self.tile_y = tile_y
        self.tile_width = tile_width
        self.tile_height = tile_height
        self.interaction = interaction
        
        image = pygame.image.load(os.path.join("assets", "features", path)).convert_alpha()
        image = pygame.transform.scale(image, (tile_width * TILE_SIZE, tile_height * TILE_SIZE))
        self.image = image
    
    def add_collision_to_world(self, map: "Map"):
        # For every tile in the image with over 50% opaque pixels, add collision to a corresponding tile
        for x in range(self.tile_width):
            for y in range(self.tile_height):
                tile_x = self.tile_x + x
                tile_y = self.tile_y + y
                if tile_x < 0 or tile_x >= MAP_WIDTH or tile_y < 0 or tile_y >= MAP_HEIGHT:
                    continue
                tile = map.tiles[tile_x * MAP_HEIGHT + tile_y]
                pixel_count = 0
                for i in range(TILE_SIZE):
                    for j in range(TILE_SIZE):
                        if self.image.get_at((x * TILE_SIZE + i, y * TILE_SIZE + j))[3] > 128:
                            pixel_count += 1
                if pixel_count / (TILE_SIZE * TILE_SIZE) > 0.5:
                    tile.collidable = True
    
    def get_interaction(self, selection_x: int, selection_y: int):
        if self.interaction and selection_x >= self.tile_x and selection_x < self.tile_x + self.tile_width and selection_y >= self.tile_y and selection_y < self.tile_y + self.tile_height:
            return self.interaction
    
    def check_proximity_interaction(self, player: "Player") -> Optional[Callable[[], None]]:
        """Returns the interaction function if the player is close enough to interact with the feature."""
        if self.interaction:
            interaction_min_x = self.tile_x * TILE_SIZE
            interaction_max_x = (self.tile_x + self.tile_width) * TILE_SIZE
            interaction_min_y = (self.tile_y + self.tile_height * 0.5) * TILE_SIZE
            interaction_max_y = (self.tile_y + self.tile_height * 1.5) * TILE_SIZE
            
            min_x, min_y, max_x, max_y = player.get_collision_rect()
            if interaction_min_x < max_x and interaction_max_x > min_x and interaction_min_y < max_y and interaction_max_y > min_y:
                return self.interaction
        return None
    
    def draw(self, win: pygame.Surface, camera_pos: pygame.Vector2, player: "Player", interaction_image: pygame.Surface):
        if self.check_proximity_interaction(player) != None:
            bottom_center_tile_x = self.tile_x * TILE_SIZE + (self.tile_width // 2) * TILE_SIZE
            bottom_center_tile_y = (self.tile_y + self.tile_height) * TILE_SIZE
            win.blit(interaction_image, (bottom_center_tile_x - camera_pos.x + get_width() // 2, bottom_center_tile_y - camera_pos.y + get_height() // 2 - TILE_SIZE))
        
        win.blit(self.image, (self.tile_x * TILE_SIZE - camera_pos.x + get_width() // 2, self.tile_y * TILE_SIZE - camera_pos.y + get_height() // 2))