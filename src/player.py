import pygame
from constants import WIDTH, HEIGHT, TILE_SIZE
from map import MAP_WIDTH, MAP_HEIGHT, Map
from items import Item, render_item_slot, get_slot_bounds
from graphics import add_floating_text_hint, FloatingHintText
import os
import math

from utils import lerp

class Player:
    pos: pygame.Vector2
    radius: int
    speed: int
    
    image: pygame.Surface
    current_image: pygame.Surface
    flipped: bool
    
    animation_frame: int
    animation_timer: float
    target_angle: float
    angle: float
    
    items: dict[Item, int]
    sold_items: dict
    
    selected_slot: int
    slot_selection_floating_text: FloatingHintText
    
    profit: int
    currency: int
    
    wait_for_mouseup: bool
    
    def __init__(self, x, y, r=16):
        self.pos = pygame.Vector2(x, y)
        self.radius = r
        self.speed = 300 # Pixels per second

        self.image_horizontal = pygame.transform.scale(img := pygame.image.load(os.path.join("assets", "sprites", "player_walk.png")).convert_alpha(), (img.get_width() * 4, img.get_height() * 4))
        self.image_down = pygame.transform.scale(img := pygame.image.load(os.path.join("assets", "sprites", "player_walk_down.png")).convert_alpha(), (img.get_width() * 4, img.get_height() * 4))
        self.image_up = pygame.transform.scale(img := pygame.image.load(os.path.join("assets", "sprites", "player_walk_up.png")).convert_alpha(), (img.get_width() * 4, img.get_height() * 4))
        self.dir_image = self.image_horizontal
        self.current_image = None
        self.flipped = False
        self.animation_frame = 0
        self.animation_timer = 0

        self.target_angle = 0
        self.angle = 0

        self.items = {}
        # self.items[Item.HOE] = 1
        # self.items[Item.AXE] = 1
        # self.items[Item.SHOVEL] = 1
        # self.items[Item.WATERING_CAN_EMPTY] = 1
        
        # # TEMPORARY
        # self.items[Item.CARROT] = 10
        # self.items[Item.ONION] = 10
        # self.items[Item.WHEAT] = 10
        # self.items[Item.CARROT_SEEDS] = 15
        # self.items[Item.ONION_SEEDS] = 15
        # self.items[Item.WHEAT_SEEDS] = 15
        # self.items[Item.WALL] = 20

        self.sold_items = {}
        
        self.selected_slot = 0
        self.slot_selection_floating_text = None

        self.profit = 0
        self.currency = 5000
        
        # Set after running out of an item so the player doesn't
        # accidentally start using the next item available.
        self.wait_for_mouseup = False
    
    def sell_items(self):
        self.sold_items = {}

        self.profit = 0

        # TODO: Wtf
        self.profit += Item.CARROT.shop_data.sell_price * self.items[Item.CARROT]
        self.sold_items[Item.CARROT] = self.items[Item.CARROT] if Item.CARROT in self.items else 0
        self.items[Item.CARROT] = 0
        self.profit += Item.ONION.shop_data.sell_price * self.items[Item.ONION]
        self.sold_items[Item.ONION] = self.items[Item.ONION] if Item.ONION in self.items else 0
        self.items[Item.ONION] = 0
        self.profit += Item.WHEAT.shop_data.sell_price * self.items[Item.WHEAT]
        self.sold_items[Item.WHEAT] = self.items[Item.WHEAT] if Item.WHEAT in self.items else 0
        self.items[Item.WHEAT] = 0

        self.currency += self.profit
    def get_sold(self, item_type):
        return self.sold_items[item_type] if item_type in self.sold_items else 0

    def update_slot_selection(self, dy):
        selected_slot = self.selected_slot + dy

        interactable_items = len(self.get_interactable_items())
        selected_slot %= interactable_items

        if selected_slot < 0:
            selected_slot += interactable_items
        
        self.select_slot(selected_slot)
    
    def select_slot(self, slot):
        if slot == self.selected_slot:
            return
        self.selected_slot = slot
        
        if self.slot_selection_floating_text != None:
            self.slot_selection_floating_text.manually_finished = True
        self.slot_selection_floating_text = FloatingHintText(
            self.get_selected_item().item_name,
            (WIDTH // 2, HEIGHT - 150),
            "white",
            -5, 1.5, 0.25, False
        )
        add_floating_text_hint(self.slot_selection_floating_text)
    
    def update(self, movement_x: float, movement_y: float, farm: Map, delta: float):        
        move = pygame.Vector2(movement_x, movement_y)

        if move.magnitude_squared() > 0:
            self.animation_timer += delta * move.magnitude()
            self.dir_image = self.image_horizontal
            if movement_x != 0.0:
                self.flipped = movement_x < 0
            else:
                if movement_y > 0:
                    self.dir_image = self.image_down
                elif movement_y < 0:
                    self.dir_image = self.image_up
        else:
            self.animation_frame = 0
        if self.animation_timer >= 0.20:
            self.animation_timer -= 0.20
            self.animation_frame = (self.animation_frame + 1) % 4
        self.current_image = self.dir_image.subsurface((64 * self.animation_frame, 0, 64, 128))

        if move.magnitude() > 0:
            self.target_angle = 270 - math.degrees(math.atan2(move.y, move.x))

        if self.target_angle > self.angle + 180:
            self.target_angle -= 360
        if self.target_angle < self.angle - 180:
            self.target_angle += 360

        self.angle = lerp(self.angle, self.target_angle, 0.1)

        move *= self.speed * delta

        # Scuffed collision
        originally_colliding = self.is_colliding(farm)
        
        old_pos = self.pos.copy()
        self.pos[0] += move[0]
        if not originally_colliding and (pos := self.is_colliding(farm)):
            self.pos = old_pos
        
        old_pos = self.pos.copy()
        self.pos[1] += move[1]
        if not originally_colliding and (pos := self.is_colliding(farm)):
            self.pos = old_pos

        # Clamp player to map
        if self.pos.x <= 0:
            self.pos.x = 0
        if self.pos.x >= MAP_WIDTH * TILE_SIZE:
            self.pos.x = MAP_WIDTH * TILE_SIZE
        
        if self.pos.y <= 0:
            self.pos.y = 0
        if self.pos.y >= MAP_HEIGHT * TILE_SIZE:
            self.pos.y = MAP_HEIGHT * TILE_SIZE

        # Ensure selected slot is within bounds
        interactable_items = len(self.get_interactable_items())
        if self.selected_slot >= interactable_items:
            self.selected_slot = interactable_items - 1

    def is_colliding(self, map):
        min_x, min_y, max_x, max_y = self.pos.x - self.radius, self.pos.y - self.radius * 2, self.pos.x + self.radius, self.pos.y + self.radius * 1.25
        min_tile_x = int(min_x // TILE_SIZE)
        min_tile_y = int(min_y // TILE_SIZE)
        max_tile_x = int(max_x // TILE_SIZE)
        max_tile_y = int(max_y // TILE_SIZE)
        for x in range(min_tile_x, max_tile_x+1):
            for y in range(min_tile_y, max_tile_y+1):
                if map.is_collision(x, y):
                    return x, y
        return None

    def over_ui(self, x, y):
        """Returns if the mouse is over the inventory UI"""
        for i in range(len(self.get_interactable_items())):
            if pygame.Rect(get_slot_bounds(i, 0, True, True)).collidepoint((x, y)):
                return True
        return False

    def mouse_down(self):
        """Returns if an interaction was inventory registered"""
        x, y = pygame.mouse.get_pos()
        
        for i in range(len(self.get_interactable_items())):
            if pygame.Rect(get_slot_bounds(i, 0, True, True)).collidepoint((x, y)):
                self.select_slot(i)
                return True
        
        return False

    def get_item_list(self) -> list[tuple[Item, int]]:
        return list(filter(lambda val: val[1] > 0, sorted(self.items.items(), key=lambda x: x[0].name)))
    def get_selected_item(self) -> Item:
        if len(self.get_interactable_items()) == 0:
            return None
        return self.get_interactable_items()[self.selected_slot][0]
    def decrement_selected_item_quantity(self):
        item = self.get_selected_item()
        if item == None:
            return
        
        self.items[item] -= 1
        if self.items[item] == 0:
            self.wait_for_mouseup = True
    def get_interactable_items(self):
        return [item for item in self.get_item_list() if item[0].interactable]
    def get_non_interactable_items(self):
        return [items for items in self.get_item_list() if not items[0].interactable]

    def draw_player(self, win, camera_pos):
        if self.current_image != None:
            win.blit(t := pygame.transform.flip(self.current_image, self.flipped, False), (self.pos.x + WIDTH // 2 - t.get_width() // 2 - camera_pos.x, self.pos.y + HEIGHT // 2 - t.get_height() // 2 - camera_pos.y - self.radius))
    
    def draw_ui(self, win):
        for i, (item, amount) in enumerate(self.get_non_interactable_items()):
            render_item_slot(win, item, amount, False, i, 0, False, True)
        for i, (item, amount) in enumerate(self.get_interactable_items()):
            render_item_slot(win, item, amount, i == self.selected_slot, i, 0, True, True)