import random
import pygame
from typing import TYPE_CHECKING, Callable, Optional
import os

from constants import FARMABLE_MAP_END, FARMABLE_MAP_START, MAP_HEIGHT, MAP_WIDTH, TILE_SIZE
from .tile import SoilStructure 
from graphics import get_height, get_width
from utils import get_asset

if TYPE_CHECKING:
    from player import Player
    from map import Map


class Entity:
    """A entity is an image placed in the world that can be interacted with."""
    x: int
    y: int
    width: int
    height: int
    collision_height: int # If 0, entity has no collision
    
    image: pygame.Surface
    interaction: Optional[Callable[[], None]]
    
    def __init__(self, x: int, y: int, width: int, height: int, path: str, interaction: Optional[Callable[[], None]] = None, collision_height: Optional[int] = None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.interaction = interaction
        self.collision_height = collision_height if collision_height != None else height
        
        image = pygame.image.load(get_asset("entities", path)).convert_alpha()
        image = pygame.transform.scale(image, (width, height))
        self.image = image
    
    def get_interaction(self, selection_x: int, selection_y: int):
        if self.interaction:
            tile_x = self.x // TILE_SIZE
            tile_y = self.y // TILE_SIZE
            width_tiles = self.width // TILE_SIZE
            height_tiles = self.height // TILE_SIZE
            if selection_x >= tile_x and selection_x < tile_x + width_tiles and selection_y >= tile_y and selection_y < tile_y + height_tiles:
                return self.interaction
        return None
    
    def get_interaction_rect(self) -> tuple[int, int, int, int]:
        """Returns the rectangle that the player must be in to interact with the entity, in the form (min_x, min_y, max_x, max_y)."""
        return self.x, self.y + self.height * 0.5, self.x + self.width, self.y + self.height * 1.5
    
    def get_collision_rect(self) -> Optional[pygame.Rect]:
        """Returns the rectangle that the entity occupies"""
        if self.collision_height == 0:
            return None
        return pygame.Rect(self.x, self.y + self.height - self.collision_height, self.width, self.collision_height)
    
    def check_proximity_interaction(self, player: "Player") -> Optional[Callable[[], None]]:
        """Returns the interaction function if the player is close enough to interact with the entity."""
        if self.interaction:
            interaction_min_x, interaction_min_y, interaction_max_x, interaction_max_y = self.get_interaction_rect()
            min_x, min_y, max_x, max_y = player.get_collision_rect()
            if interaction_min_x < max_x and interaction_max_x > min_x and interaction_min_y < max_y and interaction_max_y > min_y:
                return self.interaction
        return None
    
    def update(self, delta: float, map: "Map"):
        pass
        
    def draw(self, win: pygame.Surface, camera_pos: pygame.Vector2, player: "Player", interaction_image: pygame.Surface):
        if self.check_proximity_interaction(player) != None:
            bottom_center_tile_x = self.x + (self.width / TILE_SIZE) // 2 * TILE_SIZE
            bottom_center_tile_y = self.y + self.height
            win.blit(interaction_image, (bottom_center_tile_x - camera_pos.x + get_width() // 2, bottom_center_tile_y - camera_pos.y + get_height() // 2 - TILE_SIZE))
        
        win.blit(self.image, (self.x - camera_pos.x + get_width() // 2, self.y - camera_pos.y + get_height() // 2))


SHADOW_MACHINE_FRAME_COUNT = 5
MOVE_CHANCE_PER_SECOND = 0.7
MOVE_AMOUNT = 4
shadow_machine_sprite_sheet = pygame.image.load(get_asset("entities", "sillyguy.png")).convert_alpha()
shadow_machine_frames = []
for i in range(SHADOW_MACHINE_FRAME_COUNT):
    subsurface = shadow_machine_sprite_sheet.subsurface(pygame.Rect(i * 16, 0, 16, 16))
    shadow_machine_frames.append(pygame.transform.scale(subsurface, (TILE_SIZE, TILE_SIZE)))

class ShadowMachine(Entity):
    frame_index: int
    target: Optional[tuple[int, int]]
    speed: float # Pixels per second, scaled by distance until getting close
    
    def __init__(self):
        self.x = random.randint(FARMABLE_MAP_START[0], FARMABLE_MAP_END[0]) * TILE_SIZE
        self.y = random.randint(FARMABLE_MAP_START[1], FARMABLE_MAP_END[1]) * TILE_SIZE
        
        self.target = None
        
        self.width = TILE_SIZE
        self.height = TILE_SIZE
        self.interaction = None
        self.collision_height = 0
        
        self.speed = 150
        
        self.frame_index = random.randint(0, SHADOW_MACHINE_FRAME_COUNT - 1)
        self.image = shadow_machine_frames[self.frame_index]
    
    def update(self, delta: float, map: "Map"):
        self.frame_index = (self.frame_index + 1) % len(shadow_machine_frames)
        self.image = shadow_machine_frames[self.frame_index]
        
        if self.target:
            target_x, target_y = self.target
            move_vector = pygame.Vector2(target_x - self.x, target_y - self.y)
            distance = move_vector.length()
            if distance > 5:
                direction = move_vector.normalize()
                self.x += direction.x * self.speed * delta * max(1, distance / 10)
                self.y += direction.y * self.speed * delta * max(1, distance / 10)
            else:
                self.target = None
        else:
            if random.random() < MOVE_CHANCE_PER_SECOND * delta:
                new_target = (-1, -1)
                while new_target[0] < FARMABLE_MAP_START[0] or new_target[0] >= FARMABLE_MAP_END[0] or new_target[1] < FARMABLE_MAP_START[1] or new_target[1] >= FARMABLE_MAP_END[1]:
                    new_target = (self.x // TILE_SIZE + random.randint(-MOVE_AMOUNT, MOVE_AMOUNT), self.y // TILE_SIZE + random.randint(-MOVE_AMOUNT, MOVE_AMOUNT))
                self.target = (new_target[0] * TILE_SIZE, new_target[1] * TILE_SIZE)
        tile_x = self.x // TILE_SIZE
        tile_y = self.y // TILE_SIZE
        tile_index = int(tile_x * MAP_HEIGHT + tile_y)
        print(f"tile_index: {tile_index}, map.tiles length: {len(map.tiles)}")
        if isinstance(map.tiles[tile_index].structure, SoilStructure):
            map.tiles[tile_index].structure.should_destroy = True
    def draw(self, win: pygame.Surface, camera_pos: pygame.Vector2, player: "Player", interaction_image: pygame.Surface):
        shake = 2
        self.image.set_alpha(random.randint(130, 170))
        win.blit(self.image, (self.x - camera_pos.x + get_width() // 2 + random.randint(-shake, shake), self.y - camera_pos.y + get_height() // 2 + random.randint(-shake, shake)))