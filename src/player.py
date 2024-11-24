import pygame
from constants import WIDTH, HEIGHT, TILE_SIZE
from map import MAP_WIDTH, MAP_HEIGHT
from items import ITEM_NAMES, ITEM_TYPE, render_item_slot, is_interactable, get_slot_bounds, item_prices
from graphics import add_floating_text_hint, FloatingHintText
import os
import math

class Player:
    def __init__(self, x, y, r=16):
        self.pos = pygame.Vector2(x, y)
        self.radius = r
        self.speed = 300 # Pixels per second

        self.image = pygame.transform.scale(img := pygame.image.load(os.path.join("assets", "sprites", "player.png")), (img.get_width() * 4, img.get_height() * 4))
        self.frame = 0
        self.timer = 0

        self.angle = 0

        self.items = {}
        self.items[ITEM_TYPE.HOE] = 1
        # TEMPORARY
        self.items[ITEM_TYPE.ONION] = 17
        self.items[ITEM_TYPE.WHEAT] = 4
        self.items[ITEM_TYPE.CARROT] = 10
        self.items[ITEM_TYPE.CARROT_SEEDS] = 24
        self.items[ITEM_TYPE.ONION_SEEDS] = 10
        self.items[ITEM_TYPE.WHEAT_SEEDS] = 11
        self.items[ITEM_TYPE.WALL] = 20

        self.old_items = {}
        
        self.selected_slot = 0
        self.slot_selection_floating_text = None

        self.profit = 0
        self.currency = 0
    
    def sell_items(self):
        self.old_items = self.items.copy()

        self.profit = 0

        self.profit += item_prices[ITEM_TYPE.CARROT] * self.items[ITEM_TYPE.CARROT]
        self.items[ITEM_TYPE.CARROT] = 0
        self.profit += item_prices[ITEM_TYPE.ONION] * self.items[ITEM_TYPE.ONION]
        self.items[ITEM_TYPE.ONION] = 0
        self.profit += item_prices[ITEM_TYPE.WHEAT] * self.items[ITEM_TYPE.WHEAT]
        self.items[ITEM_TYPE.WHEAT] = 0

        self.currency += self.profit

        self.current_image = None

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
            "black",
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

            self.angle = 270 - math.degrees(math.atan2(move.y, move.x))

        move *= self.speed * delta
        # Scuffed collision
        old_pos = self.pos
        self.pos[0] += move[0]
        if self.is_colliding(map):
            self.pos = old_pos
        old_pos = self.pos
        self.pos[1] += move[1]
        if self.is_colliding(map):
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
        possible_range = self.radius // TILE_SIZE + 1
        for i in range(-possible_range, possible_range + 1):
            for j in range(-possible_range, possible_range + 1):
                if map.is_collision(self.pos.x // TILE_SIZE + i, self.pos.y // TILE_SIZE + j):
                    return pygame.Rect(i * TILE_SIZE, j * TILE_SIZE, TILE_SIZE, TILE_SIZE).colliderect(
                        self.pos.x - self.radius, self.pos.y - self.radius, self.radius * 2, self.radius * 2
                    )
        return False

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
        self.items[self.get_selected_item()[0]] -= 1
    def get_interactable_items(self):
        return [item for item in self.get_item_list() if is_interactable(item[0])]
    def get_non_interactable_items(self):
        return [items for items in self.get_item_list() if not is_interactable(items[0])]

    def draw_player(self, win):
        # pygame.draw.circle(win, 'violet', (WIDTH // 2, HEIGHT // 2), self.radius)
        win.blit(t := pygame.transform.rotate(self.current_image, self.angle), (WIDTH // 2 - t.get_width() // 2, HEIGHT // 2 - t.get_height() // 2))

    def draw_ui(self, win):
        for i, (item, amount) in enumerate(self.get_non_interactable_items()):
            render_item_slot(win, item, amount, False, i, 0, False, True)
        for i, (item, amount) in enumerate(self.get_interactable_items()):
            render_item_slot(win, item, amount, i == self.selected_slot, i, 0, True, True)