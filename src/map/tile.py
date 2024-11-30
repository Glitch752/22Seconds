from abc import ABC
from enum import Enum, IntEnum, auto
import random
from typing import Optional, TYPE_CHECKING

import pygame

from audio import AudioManager, SoundType
from constants import PARTICLES_PER_TILE_SECOND, TILE_SIZE
from graphics.floating_hint_text import FloatingHintText, add_floating_text_hint
from graphics.particles import spawn_particles_in_square
from items import Item, ItemHarvestData

if TYPE_CHECKING:
    from player import Player

class Structure(ABC):
    def __init__(self):
        pass
    
    def random_tick(self, audio_manager: AudioManager):
        pass
    
    def get_interaction(self, item: Item, player: "Player", audio_manager: AudioManager, tile_center_pos: tuple[int, int]):
        """
        Returns a lambda that will execute the proper interaction based on the selected tile and item,
        or None if no interaction should occur.
        """
        pass
    
    def draw(self, win: pygame.Surface, x, y, tile_center_pos: tuple[int, int], delta: float):
        """
        x and y are screen coordinates, while tile_center_pos is the center of the tile in world coordinates.
        """
        pass

plant_images = {
    Item.CARROT_SEEDS: [],
    Item.WHEAT_SEEDS: [],
    Item.ONION_SEEDS: []
}

MAX_PLANT_GROWTH_STAGE = 2
for plant_type in plant_images:
    plant_names = {
        Item.CARROT_SEEDS: "carrot",
        Item.WHEAT_SEEDS: "wheat",
        Item.ONION_SEEDS: "onion"
    }
    for i in range(MAX_PLANT_GROWTH_STAGE + 1):
        image = pygame.image.load(f"assets/tiles/planted_{plant_names[plant_type]}_{i}.png").convert_alpha()
        image = pygame.transform.scale(image, (TILE_SIZE, TILE_SIZE))
        plant_images[plant_type].append(image)

dry_soil_image = pygame.transform.scale(
    pygame.image.load("assets/tiles/farmland.png").convert_alpha(),
    (TILE_SIZE, TILE_SIZE)
)
wet_soil_image = pygame.transform.scale(
    pygame.image.load("assets/tiles/wet_farmland.png").convert_alpha(),
    (TILE_SIZE, TILE_SIZE)
)

class SoilStructure(Structure):
    """
    Soil structures can have plants growing on them.
    """
    item: Optional[Item]
    growth_stage: int = 0
    wet: bool = False
    
    def __init__(self, item: Optional[Item]):
        self.item = item
    
    def random_tick(self, audio_manager: AudioManager):
        if self.item != None and self.growth_stage < MAX_PLANT_GROWTH_STAGE:
            if not self.wet:
                if random.random() <= 0.5:
                    return
            else:
                if random.random() <= 0.1:
                    self.wet = False
            self.growth_stage += 1
            # audio_manager.play_sound(SoundType.PLANT) # TODO: Better growth sound
    
    def put_seed(self, item: Item, player: "Player", audio_manager: AudioManager, tile_center_pos: tuple[int, int]):
        player.decrement_selected_item_quantity()
        self.item = item
        self.growth_stage = 0
        audio_manager.play_sound(SoundType.PLANT)
        
        tile_center_pos = (tile_center_pos[0], tile_center_pos[1] - TILE_SIZE)
        add_floating_text_hint(FloatingHintText(f"-1 {item.harvest_data.name}", tile_center_pos, "orange"))
    
    def harvest(self, player: "Player", audio_manager: AudioManager, tile_center_pos: tuple[int, int]):
        audio_manager.play_sound(SoundType.HARVEST_PLANT)

        v = random.random()
        if v <= 0.1:
            # 10% chance of harvesting 1
            r = 1
        elif v <= 0.9:
            # 80% chance of harvesting 2
            r = 2
        else:
            # 10% chance of harvesting 3
            r = 3
        
        harvest_data: ItemHarvestData = self.item.harvest_data
        tile_center_pos = (tile_center_pos[0], tile_center_pos[1] - TILE_SIZE)
        add_floating_text_hint(FloatingHintText(f"+{r} {harvest_data.name}", tile_center_pos, harvest_data.grown_particle_color))
        player.items[harvest_data.harvest_item] += r
        
        self.item = None
        self.growth_stage = 0
    
    def make_wet(self, tile_center_pos, player: "Player", audio_manager: AudioManager):
        self.wet = True
        player.items[Item.WATERING_CAN_FULL] -= 1
        if player.items[Item.WATERING_CAN_FULL] == 0:
            player.items[Item.WATERING_CAN_EMPTY] = 1
        audio_manager.play_sound(SoundType.WATER)
        add_floating_text_hint(FloatingHintText(f"Watered!", tile_center_pos, "skyblue"))
    
    def get_interaction(self, item: Item, player: "Player", audio_manager: AudioManager, tile_center_pos: tuple[int, int]):
        if item in {Item.CARROT_SEEDS, Item.WHEAT_SEEDS, Item.ONION_SEEDS} and self.item == None:
            return lambda: self.put_seed(item, player, audio_manager, tile_center_pos)
        
        if item == Item.HOE and self.item != None and self.growth_stage == MAX_PLANT_GROWTH_STAGE:
            return lambda: self.harvest(player, audio_manager, tile_center_pos)
        
        if item == Item.WATERING_CAN_FULL and not self.wet:
            return lambda: self.make_wet(tile_center_pos, player, audio_manager)
        
        return None
    
    def draw(self, win: pygame.Surface, x: int, y: int, tile_center_pos: tuple[int, int], delta: float):
        win.blit(wet_soil_image if self.wet else dry_soil_image, (x, y))
        if self.item != None:
            win.blit(plant_images[self.item][self.growth_stage], (x, y))
        
        if self.item != None and self.growth_stage == MAX_PLANT_GROWTH_STAGE and random.random() < delta * PARTICLES_PER_TILE_SECOND:
            plant_particle_colors = {
                Item.CARROT_SEEDS: "orange",
                Item.WHEAT_SEEDS: "yellow",
                Item.ONION_SEEDS: "purple"
            }
            spawn_particles_in_square(tile_center_pos[0], tile_center_pos[1], plant_particle_colors[self.item], TILE_SIZE//2, 1)

class TileType(Enum):
    """
    Tiles with a higher layer are drawn on top of earlier ones.
    """
    WATER = "assets/tiles/water_tilemap.png", 0
    OUTSIDE_FARM_DIRT = "assets/tiles/outside_farm_dirt_tilemap.png", 1
    SOIL = "assets/tiles/dirt_tilemap.png", 2
    GRASS = "assets/tiles/grass_tilemap.png", 3
    TALL_GRASS = "assets/tiles/tall_grass_tilemap.png", 4
    
    path: str
    atlas: list[pygame.Surface]
    layer: int

    def __new__(cls, *args, **kwds):
        value = len(cls.__members__) + 1
        obj = object.__new__(cls)
        obj._value_ = value
        return obj
    def __init__(self, path: str, layer: int):
        self.path = path
        self.layer = layer
        
        tilemap_image = pygame.image.load(self.path).convert_alpha()
        tilemap_atlas = []
        # For each of the 16 possible combinations of yes/no for the 4 corners of a tile,
        # we fill the tilemap atlas position 0b(top left)(top right)(bottom left)(bottom right)
        image_size = tilemap_image.get_width()
        # There are definitely more efficient ways to calculate this,
        # but this was easy to copy...
        atlas_positions = {
            (True, True, True, True): (2, 1),     # All corners
            (False, False, False, True): (1, 3),  # Outer bottom-right corner
            (False, False, True, False): (0, 0),  # Outer bottom-left corner
            (False, True, False, False): (0, 2),  # Outer top-right corner
            (True, False, False, False): (3, 3),  # Outer top-left corner
            (False, True, False, True): (1, 0),   # Right edge
            (True, False, True, False): (3, 2),   # Left edge
            (False, False, True, True): (3, 0),   # Bottom edge
            (True, True, False, False): (1, 2),   # Top edge
            (False, True, True, True): (1, 1),    # Inner bottom-right corner
            (True, False, True, True): (2, 0),    # Inner bottom-left corner
            (True, True, False, True): (2, 2),    # Inner top-right corner
            (True, True, True, False): (3, 1),    # Inner top-left corner
            (False, True, True, False): (2, 3),   # Bottom-left top-right corners
            (True, False, False, True): (0, 1),   # Top-left down-right corners
            (False, False, False, False): (0, 3), # No corners
        }
        for i in range(16):
            corner_values = [(i & (1 << j)) != 0 for j in range(4)]
            pos = atlas_positions[(*corner_values,)]
            
            atlas_image = tilemap_image.subsurface(pos[0] * image_size // 4, pos[1] * image_size // 4, image_size // 4, image_size // 4)
            atlas_image = pygame.transform.scale(atlas_image, (TILE_SIZE, TILE_SIZE))
            tilemap_atlas.append(atlas_image)
        self.atlas = tilemap_atlas

class Tile:
    structure: Optional[Structure]
    tile_type: TileType
    collidable: bool = False
    
    def __init__(self, tile_type: TileType):
        self.structure = None
        self.tile_type = tile_type
        self.collidable = self.tile_type in [TileType.WATER]

    def is_collidable(self):
        return self.collidable
    
    def draw(self, win: pygame.Surface, x: int, y: int, tile_center_pos: tuple[int, int], delta: float):
        """
        Draws everything on this tile, but not the tile itself.
        Tile rendering uses a dual-grid system, so it's handled at the map level.
        x and y are screen coordinates, while tile_center_pos is the center of the tile in world coordinates.
        """
        if self.structure:
            self.structure.draw(win, x, y, tile_center_pos, delta)
    
    def tilled(self, tile_center_pos: tuple[int, int], audio_manager: AudioManager):
        self.structure = SoilStructure(None)
        audio_manager.play_sound(SoundType.TILL_SOIL)
        add_floating_text_hint(FloatingHintText(f"Tilled soil!", tile_center_pos, "white"))
    
    def shoveled(self, tile_center_pos: tuple[int, int], audio_manager: AudioManager):
        self.tile_type = TileType.SOIL
        audio_manager.play_sound(SoundType.TILL_SOIL) # TODO: Shovel sound
        add_floating_text_hint(FloatingHintText(f"Shoveled ground!", tile_center_pos, "white"))
    
    def fill_watering_can(self, player: "Player", tile_center_pos: tuple[int, int], audio_manager: AudioManager):
        player.items[Item.WATERING_CAN_EMPTY] = 0
        player.items[Item.WATERING_CAN_FULL] = 5
        audio_manager.play_sound(SoundType.WATER) # TODO: water fill sound
        add_floating_text_hint(FloatingHintText(f"Filled can!", tile_center_pos, "skyblue"))
    
    def get_interaction(self, item: Item, player: "Player", audio_manager: AudioManager, tile_center_pos: tuple[int, int]):
        """
        Returns a lambda that will execute the proper interaction based on the selected tile and item,
        or None if no interaction should occur.
        """
        
        if self.structure:
            return self.structure.get_interaction(item, player, audio_manager, tile_center_pos)
        
        match (self.tile_type, item):
            case (TileType.SOIL, Item.HOE):
                return (lambda: self.tilled(tile_center_pos, audio_manager))
            case (TileType.GRASS | TileType.TALL_GRASS, Item.SHOVEL):
                return (lambda: self.shoveled(tile_center_pos, audio_manager))
            case (TileType.WATER, Item.WATERING_CAN_EMPTY):
                return (lambda: self.fill_watering_can(player, tile_center_pos, audio_manager))
            case _:
                pass
        
        return None
    
    def random_tick(self, audio_manager: AudioManager):
        if self.structure:
            self.structure.random_tick(audio_manager)