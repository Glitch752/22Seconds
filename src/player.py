import pygame
from constants import WIDTH, HEIGHT, TILE_SIZE, lerp
from map import MAP_WIDTH, MAP_HEIGHT, TILE_TYPE
from items import ITEM_NAMES, ITEM_TYPE, render_item_slot, is_interactable, get_slot_bounds, item_prices
from graphics import add_floating_text_hint, FloatingHintText
import os
import math

class Player:
    def __init__(self, x, y, r=16):
        self.pos = pygame.Vector2(x, y)
        self.radius = r
        self.speed = 300 # Pixels per second

        self.image = pygame.transform.scale(img := pygame.image.load(os.path.join("assets", "sprites", "player_normal.png")), (img.get_width() * 4, img.get_height() * 4))
        self.current_image = None
        self.frame = 0
        self.timer = 0

        self.target_angle = 0
        self.angle = 0

        self.items = {}
        self.items[ITEM_TYPE.HOE] = 1
        self.items[ITEM_TYPE.AXE] = 1
        self.items[ITEM_TYPE.SHOVEL] = 1
        self.items[ITEM_TYPE.WATERING_CAN_EMPTY] = 1
        # TEMPORARY
        self.items[ITEM_TYPE.CARROT] = 25
        self.items[ITEM_TYPE.ONION] = 0
        self.items[ITEM_TYPE.WHEAT] = 0
        self.items[ITEM_TYPE.CARROT_SEEDS] = 30
        self.items[ITEM_TYPE.ONION_SEEDS] = 0
        self.items[ITEM_TYPE.WHEAT_SEEDS] = 0
        self.items[ITEM_TYPE.WALL] = 20

        self.sold_items = {}
        
        self.selected_slot = 0
        self.slot_selection_floating_text = None

        self.profit = 0
        self.currency = 0
        
        # Set after running out of an item so the player doesn't
        # accidentally start using the next item available.
        self.wait_for_mouseup = False
    
    def sell_items(self):
        self.sold_items = {}

        self.profit = 0

        # TODO: Wtf
        self.profit += item_prices[ITEM_TYPE.CARROT] * self.items[ITEM_TYPE.CARROT]
        self.sold_items[ITEM_TYPE.CARROT] = self.items[ITEM_TYPE.CARROT] if ITEM_TYPE.CARROT in self.items else 0
        self.items[ITEM_TYPE.CARROT] = 0
        self.profit += item_prices[ITEM_TYPE.ONION] * self.items[ITEM_TYPE.ONION]
        self.sold_items[ITEM_TYPE.ONION] = self.items[ITEM_TYPE.ONION] if ITEM_TYPE.ONION in self.items else 0
        self.items[ITEM_TYPE.ONION] = 0
        self.profit += item_prices[ITEM_TYPE.WHEAT] * self.items[ITEM_TYPE.WHEAT]
        self.sold_items[ITEM_TYPE.WHEAT] = self.items[ITEM_TYPE.WHEAT] if ITEM_TYPE.WHEAT in self.items else 0
        self.items[ITEM_TYPE.WHEAT] = 0

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
            ITEM_NAMES[self.get_selected_item()[0]],
            (WIDTH // 2, HEIGHT - 150),
            "white",
            -5, 1.5, 0.25, False
        )
        add_floating_text_hint(self.slot_selection_floating_text)
    
    def update(self, mx, my, map, delta):
        if mx or my:
            self.timer += delta

        if self.timer >= 0.15:
            self.timer -= 0.15
            
            self.frame = (self.frame + 1) % 4
        
        self.current_image = self.image.subsurface((self.image.get_height() * self.frame, 0, self.image.get_height(), self.image.get_height()))

        move = pygame.Vector2(mx, my)

        if move.magnitude():
            move = move.normalize()

            self.target_angle = 270 - math.degrees(math.atan2(move.y, move.x))

        move *= self.speed * delta

        if self.target_angle > self.angle + 180:
            self.target_angle -= 360
        if self.target_angle < self.angle - 180:
            self.target_angle += 360

        self.angle = lerp(self.angle, self.target_angle, 0.1)

        # Scuffed collision
        originally_colliding = self.is_colliding(map)
        
        old_pos = self.pos.copy()
        self.pos[0] += move[0]
        if not originally_colliding and (pos := self.is_colliding(map)):
            self.pos = old_pos
        
        old_pos = self.pos.copy()
        self.pos[1] += move[1]
        if not originally_colliding and (pos := self.is_colliding(map)):
            self.pos = old_pos

        if self.pos.x <= 0:
            self.pos.x = 0
        if self.pos.x >= MAP_WIDTH * TILE_SIZE:
            self.pos.x = MAP_WIDTH * TILE_SIZE
        
        if self.pos.y <= 0:
            self.pos.y = 0
        if self.pos.y >= MAP_HEIGHT * TILE_SIZE:
            self.pos.y = MAP_HEIGHT * TILE_SIZE

        interactable_items = len(self.get_interactable_items())
        if self.selected_slot >= interactable_items:
            self.selected_slot = interactable_items - 1

    def is_colliding(self, map):
        min_x, min_y, max_x, max_y = self.pos.x - self.radius, self.pos.y - self.radius, self.pos.x + self.radius, self.pos.y + self.radius
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
        """Returns if the mouse is over the UI"""
        for i in range(len(self.get_interactable_items())):
            if pygame.Rect(get_slot_bounds(i, 0, True, True)).collidepoint((x, y)):
                return True
        return False

    def mouse_down(self, x, y):
        """Returns if an interaction was registered"""
        for i in range(len(self.get_interactable_items())):
            if pygame.Rect(get_slot_bounds(i, 0, True, True)).collidepoint((x, y)):
                # TODO show name of item when selecting slots (and also when scrolling)
                self.select_slot(i)
                return True
        
        return False

    def get_item_list(self):
        return list(filter(lambda val: val[1] > 0, sorted(self.items.items())))
    def get_selected_item(self):
        return self.get_interactable_items()[self.selected_slot]
    def decrement_selected_item_quantity(self):
        item = self.get_selected_item()[0]
        self.items[item] -= 1
        if self.items[item] == 0:
            self.wait_for_mouseup = True
    def get_interactable_items(self):
        return [item for item in self.get_item_list() if is_interactable(item[0])]
    def get_non_interactable_items(self):
        return [items for items in self.get_item_list() if not is_interactable(items[0])]

    def draw_player(self, win):
        win.blit(t := pygame.transform.rotate(self.current_image, self.angle), (WIDTH // 2 - t.get_width() // 2, HEIGHT // 2 - t.get_height() // 2))
        
        # r = 20

        # pygame.draw.circle(win, 'blue', (WIDTH // 2 + math.cos(math.radians(self.target_angle)) * r, HEIGHT // 2 + math.sin(math.radians(self.target_angle)) * r), 4)
        # pygame.draw.circle(win, 'red', (WIDTH // 2 + math.cos(math.radians(self.angle)) * r, HEIGHT // 2 + math.sin(math.radians(self.angle)) * r), 4)

    def draw_ui(self, win):
        for i, (item, amount) in enumerate(self.get_non_interactable_items()):
            render_item_slot(win, item, amount, False, i, 0, False, True)
        for i, (item, amount) in enumerate(self.get_interactable_items()):
            render_item_slot(win, item, amount, i == self.selected_slot, i, 0, True, True)