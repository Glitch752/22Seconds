import pygame
import graphics
from constants import WIDTH, HEIGHT
import os

ITEM_SLOT_ITEM_SIZE = 64
ITEM_SLOT_PADDING = 8
ITEM_SLOT_MARGIN = 8
ITEM_SLOT_BORDER_RADIUS = 8

class ITEM_TYPE:
    HOE = 0
    CARROT_SEEDS = 1
    WHEAT_SEEDS = 2
    ONION_SEEDS = 3
    CARROT = 4
    WHEAT = 5
    ONION = 6
    WALL = 7
    AXE = 8
    SHOVEL = 9

item_prices = {
    ITEM_TYPE.CARROT: 6, # sell
    ITEM_TYPE.ONION: 12, # sell
    ITEM_TYPE.WHEAT: 18, # sell
    ITEM_TYPE.CARROT_SEEDS: 10, # buy
    ITEM_TYPE.ONION_SEEDS: 15, # buy
    ITEM_TYPE.WHEAT_SEEDS: 20, # buy
    ITEM_TYPE.WALL: 25 # buy
}

SLOT_BACKGROUND = (48, 29, 29) # TODO: Refactor out of items since we use this for other UI
SLOT_BACKGROUND_SELECTED = (88, 59, 59)

ITEM_IMAGES = {}
INTERACTABLE_ITEMS = {}
ITEM_NAMES = {}
def add_item_data(item, path, name, interactable):
    original_image = pygame.image.load(os.path.join("assets", "sprites", path))
    image = pygame.transform.scale(original_image, (ITEM_SLOT_ITEM_SIZE, ITEM_SLOT_ITEM_SIZE))
    ITEM_IMAGES[item] = image
    INTERACTABLE_ITEMS[item] = interactable
    ITEM_NAMES[item] = name

add_item_data(ITEM_TYPE.HOE, "hoe_sprite.png", "Hoe", True)
add_item_data(ITEM_TYPE.CARROT_SEEDS, "carrot_seeds.png", "Carrot seeds", True)
add_item_data(ITEM_TYPE.WHEAT_SEEDS, "wheat_seeds.png", "Wheat seeds", True)
add_item_data(ITEM_TYPE.ONION_SEEDS, "onion_seeds.png", "Onion seeds", True)
add_item_data(ITEM_TYPE.CARROT, "carrot_sprite.png", "Carrot", False)
add_item_data(ITEM_TYPE.WHEAT, "wheat_sprite.png", "Wheat", False)
add_item_data(ITEM_TYPE.ONION, "onion_sprite.png", "Onion", False)
add_item_data(ITEM_TYPE.WALL, "wall_sprite.png", "Wall", True)
add_item_data(ITEM_TYPE.AXE, "axe_sprite.png", "Axe", True)
add_item_data(ITEM_TYPE.SHOVEL, "shovel_sprite.png", "Shovel", True)

def is_interactable(item):
    return INTERACTABLE_ITEMS[item]

def get_slot_bounds(slot_x, slot_y, anchor_bottom, anchor_right):
    total_slot_size = ITEM_SLOT_ITEM_SIZE + ITEM_SLOT_PADDING * 2 + ITEM_SLOT_MARGIN
    slot_size = ITEM_SLOT_ITEM_SIZE + ITEM_SLOT_PADDING * 2

    x = slot_x * total_slot_size + ITEM_SLOT_MARGIN
    y = slot_y * total_slot_size + ITEM_SLOT_MARGIN
    if anchor_bottom:
        y = HEIGHT - y - slot_size
    if anchor_right:
        x = WIDTH - x - slot_size
    
    return (x, y, total_slot_size, total_slot_size)

def render_item_slot(win: pygame.Surface, item, quantity, selected, slot_x, slot_y, anchor_bottom = False, anchor_right = False):
    bounds = get_slot_bounds(slot_x, slot_y, anchor_bottom, anchor_right)
    (x, y, _, _) = bounds
    slot_size = ITEM_SLOT_ITEM_SIZE + ITEM_SLOT_PADDING * 2

    pygame.draw.rect(
        win,
        SLOT_BACKGROUND_SELECTED if selected else SLOT_BACKGROUND,
        (x, y, slot_size, slot_size),
        border_radius=ITEM_SLOT_BORDER_RADIUS
    )

    item_image = ITEM_IMAGES[item]
    win.blit(item_image, (x + ITEM_SLOT_PADDING, y + ITEM_SLOT_PADDING))

    if quantity != 1:
        win.blit(
            q := graphics.small_font_render(str(quantity)),
            (x + slot_size - q.get_width() - 2, y + slot_size - q.get_height() - 2)
        )

    mouse_pos = pygame.mouse.get_pos()
    if pygame.Rect(bounds).collidepoint(mouse_pos):
        graphics.draw_deferred(lambda: graphics.draw_tooltip(win, mouse_pos, ITEM_NAMES[item]))