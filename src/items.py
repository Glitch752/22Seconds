from enum import Enum
from typing import Optional
import pygame
import graphics
from graphics import get_width, get_height
from constants import ITEM_SLOT_BORDER_RADIUS, ITEM_SLOT_ITEM_SIZE, ITEM_SLOT_MARGIN, ITEM_SLOT_PADDING, SLOT_BACKGROUND, SLOT_BACKGROUND_SELECTED
import os

class ItemShopData:
    buy_price: Optional[int]
    sell_price: Optional[int]
    def __init__(self, buy_price: Optional[int], sell_price: Optional[int] = -1):
        self.buy_price = buy_price
        self.sell_price = sell_price if sell_price != -1 else buy_price

class ItemHarvestData:
    grown_particle_color: str
    harvest_item: "Item"
    name: str
    def __init__(self, grown_particle_color: str, harvest_item: "Item"):
        self.grown_particle_color = grown_particle_color
        self.harvest_item = harvest_item
        self.name = harvest_item.item_name

class Item(Enum):
    HOE =                ("hoe_sprite.png",               "Hoe",          True,  None,                   "Can be used to till soil and\npick up fully-grown crops.")
    CARROT_SEEDS =       ("carrot_seeds.png",             "Carrot seeds", True,  ItemShopData(25),       "Used to plant carrots.")
    WHEAT_SEEDS =        ("wheat_seeds.png",              "Wheat seeds",  True,  ItemShopData(25),       "Used to plant wheat.")
    ONION_SEEDS =        ("onion_seeds.png",              "Onion seeds",  True,  ItemShopData(25),       "Used to plant onions.")
    CARROT =             ("carrot_sprite.png",            "Carrot",       False, ItemShopData(None, 25), "A delicious orange vegetable.\nCan be sold for currency.")
    WHEAT =              ("wheat_sprite.png",             "Wheat",        False, ItemShopData(None, 25), "A yellow grain.\nCan be sold for currency.")
    ONION =              ("onion_sprite.png",             "Onion",        False, ItemShopData(None, 25), "A purple vegetable.\nCan be sold for currency.")
    WALL =               ("wall_sprite.png",              "Wall",         True,  ItemShopData(25),       "Can be placed to block movement...\nWhy would you need this?")
    AXE =                ("axe_sprite.png",               "Axe",          True,  None,                   "Can be used to destroy placed walls.")
    SHOVEL =             ("shovel_sprite.png",            "Shovel",       True,  None,                   "Can turn grass into fertile soil.")
    WATERING_CAN_EMPTY = ("watering_can_sprite.png",      "Watering Can", True,  None,                   "Can be used to water crops when\nfilled with water.")
    WATERING_CAN_FULL =  ("watering_can_full_sprite.png", "Watering Can", True,  None,                   "Can be used to water crops.")
    
    image: pygame.Surface
    path: str
    item_name: str
    interactable: bool
    shop_data: Optional[ItemShopData]
    harvest_data: Optional[ItemHarvestData]
    description: str
    
    def __new__(cls, *args, **kwds):
        value = len(cls.__members__) + 1
        obj = object.__new__(cls)
        obj._value_ = value
        return obj
    def __init__(self, path: str, item_name: str, interactable: bool, shop_data: Optional[ItemShopData], description: str):
        self.path = path
        original_image = pygame.image.load(os.path.join("assets", "sprites", path)).convert_alpha()
        image = pygame.transform.scale(original_image, (ITEM_SLOT_ITEM_SIZE, ITEM_SLOT_ITEM_SIZE))
        self.image = image
        
        self.item_name = item_name
        self.interactable = interactable
        self.shop_data = shop_data
        self.harvest_data = None
        
        self.description = description
    
    @staticmethod
    def add_harvest_data(item: "Item", harvest_data: ItemHarvestData):
        item.harvest_data = harvest_data

Item.add_harvest_data(Item.CARROT_SEEDS, ItemHarvestData("orange", Item.CARROT))
Item.add_harvest_data(Item.WHEAT_SEEDS, ItemHarvestData("yellow", Item.WHEAT))
Item.add_harvest_data(Item.ONION_SEEDS, ItemHarvestData("purple", Item.ONION))

def get_slot_bounds(slot_x, slot_y, anchor_bottom, anchor_right):
    total_slot_size = ITEM_SLOT_ITEM_SIZE + ITEM_SLOT_PADDING * 2 + ITEM_SLOT_MARGIN
    slot_size = ITEM_SLOT_ITEM_SIZE + ITEM_SLOT_PADDING * 2

    x = slot_x * total_slot_size + ITEM_SLOT_MARGIN
    y = slot_y * total_slot_size + ITEM_SLOT_MARGIN
    if anchor_bottom:
        y = get_height() - y - slot_size
    if anchor_right:
        x = get_width() - x - slot_size
    
    return (x, y, total_slot_size, total_slot_size)

def render_item_slot(win: pygame.Surface, item: Item, quantity: int, selected: bool, slot_x: int, slot_y: int, anchor_bottom = False, anchor_right = False):
    bounds = get_slot_bounds(slot_x, slot_y, anchor_bottom, anchor_right)
    (x, y, _, _) = bounds
    slot_size = ITEM_SLOT_ITEM_SIZE + ITEM_SLOT_PADDING * 2

    pygame.draw.rect(
        win,
        SLOT_BACKGROUND_SELECTED if selected else SLOT_BACKGROUND,
        (x, y, slot_size, slot_size),
        border_radius=ITEM_SLOT_BORDER_RADIUS
    )

    win.blit(item.image, (x + ITEM_SLOT_PADDING, y + ITEM_SLOT_PADDING))

    if quantity != 1:
        win.blit(
            q := graphics.small_font_render(str(quantity)),
            (x + slot_size - q.get_width() - 2, y + slot_size - q.get_height() - 2)
        )

    mouse_pos = pygame.mouse.get_pos()
    if pygame.Rect(bounds).collidepoint(mouse_pos):
        tooltip_lines = [item.item_name]
        for description_line in item.description.split('\n'):
            tooltip_lines.append((description_line, 'gray'))
        # tooltip_lines.append((f"Quantity: {quantity}", "#ccaa88"))
        if item.shop_data != None:
            if item.shop_data.buy_price != None:
                tooltip_lines.append((f"Buy price: {item.shop_data.buy_price}c", "#88cc88"))
            if item.shop_data.sell_price != None:
                tooltip_lines.append((f"Sell price: {item.shop_data.sell_price}c", "#cc8888"))
        graphics.draw_deferred(lambda: graphics.draw_tooltip(win, mouse_pos, tooltip_lines))