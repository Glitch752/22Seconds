import pygame
from constants import WIDTH, HEIGHT, TILE_SIZE
from map import MAP_WIDTH, MAP_HEIGHT
from items import ITEM_NAMES, ITEM_TYPE, render_item_slot, is_interactable, get_slot_bounds
from graphics import add_floating_text_hint, FloatingHintText

class Player:
    def __init__(self, x, y, r=16):
        self.pos = pygame.Vector2(x, y)
        self.radius = r
        self.speed = 500 # Pixels per second

        self.items = {}
        self.items[ITEM_TYPE.HOE] = 1
        self.items[ITEM_TYPE.ONION] = 17
        self.items[ITEM_TYPE.CARROT_SEEDS] = 5
        self.items[ITEM_TYPE.WHEAT] = 4
        self.selected_slot = 0
        self.slot_selection_floating_text = None
    
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
    
    def update(self, mx, my, delta):
        move = pygame.Vector2(mx, my)

        if move.magnitude():
            move = move.normalize()

        move *= self.speed * delta
        self.pos += move
        
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

    def draw(self, win):
        pygame.draw.circle(win, 'violet', (WIDTH // 2, HEIGHT // 2), self.radius)

        for i, (item, amount) in enumerate(self.get_non_interactable_items()):
            render_item_slot(win, item, amount, False, i, 0, False, True)
        for i, (item, amount) in enumerate(self.get_interactable_items()):
            render_item_slot(win, item, amount, i == self.selected_slot, i, 0, True, True)