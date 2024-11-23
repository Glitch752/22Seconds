import pygame
from constants import WIDTH, HEIGHT
from items import ITEM_TYPE, render_item_slot, is_interactable, get_slot_bounds

class Player:
    def __init__(self, x, y, r=16):
        self.pos = pygame.Vector2(x, y)
        self.radius = r
        self.speed = 800 # Pixels per second

        self.items = {}
        self.items[ITEM_TYPE.HOE] = 1
        self.items[ITEM_TYPE.ONION] = 17
        self.items[ITEM_TYPE.CARROT_SEEDS] = 5
        self.items[ITEM_TYPE.WHEAT] = 4
        self.selected_slot = 0
    
    def update_slot_selection(self, dy):
        self.selected_slot += dy

        self.selected_slot %= len(self.items) - 1

        if self.selected_slot < 0:
            self.selected_slot += len(self.items)
    
    def update(self, mx, my, delta):
        move = pygame.Vector2(mx, my)

        if move.magnitude():
            move = move.normalize()

        move *= self.speed * delta
        self.pos += move

        item_list = self.get_item_list()
        if self.selected_slot >= len(item_list):
            self.selected_slot = len(item_list) - 1

    def mouse_down(self, x, y):
        """Returns if an interaction was registered"""
        for i in range(len(self.get_interactable_items())):
            if pygame.Rect(get_slot_bounds(i, 0, True, True)).collidepoint((x, y)):
                # TODO show name of item
                self.selected_slot = i
                return True
        
        return False

    def get_item_list(self):
        return sorted(self.items.items())
    def get_selected_item(self):
        return self.get_item_list()[self.selected_slot]
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