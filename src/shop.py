import pygame
import os

from constants import HEIGHT, TILE_SIZE, WIDTH
from graphics import big_font_render, normal_font_render
from ui import Button
from items import item_prices, ITEM_TYPE

buy_item_sound = pygame.mixer.Sound(os.path.join("assets", "audio", "chaChing.wav")) # TODO: Better purchase sound
eurgh_item_sound = pygame.mixer.Sound(os.path.join("assets", "audio", "Aeeaahghgh.wav")) # TODO: Better bad eurgh sound

def buy_item(item, received_quantity=1):
    from main import player
    price = item_prices[item]

    if player.currency >= price:
        player.currency -= price

        player.items[item] += received_quantity
        
        buy_item_sound.play()
    else:
        eurgh_item_sound.play()

def try_to_win_lmao():
    from main import player, set_game_state, GameState
    if player.currency >= 1000:
        set_game_state(GameState.Cutscene_Outro)
    else:
        eurgh_item_sound.play()


def exit_shop():
    from main import set_game_state, GameState, day_track
    set_game_state(GameState.Playing)
    pygame.mixer.music.stop()
    pygame.mixer.music.load(day_track)
    pygame.mixer.music.play()

shop_buttons = [
    Button(f"Buy Carrot Seed - {item_prices[ITEM_TYPE.CARROT_SEEDS]}c", WIDTH // 2, HEIGHT // 2, buy_item, (ITEM_TYPE.CARROT_SEEDS,)),
    Button(f"Buy Onion Seed - {item_prices[ITEM_TYPE.ONION_SEEDS]}c", WIDTH // 2, HEIGHT // 2 + 40, buy_item, (ITEM_TYPE.ONION_SEEDS,)),
    Button(f"Buy Wheat Seed - {item_prices[ITEM_TYPE.WHEAT_SEEDS]}c", WIDTH // 2, HEIGHT // 2 + 80, buy_item, (ITEM_TYPE.WHEAT_SEEDS,)),
    Button(f"Buy 5 Walls - {item_prices[ITEM_TYPE.WALL]}c", WIDTH // 2, HEIGHT // 2 + 120, buy_item, (ITEM_TYPE.WALL,)),
    Button(f"Pay for your medical needs - 1,000c", WIDTH // 2, HEIGHT // 2 + 160, try_to_win_lmao, ()),
    Button(f"Exit Shop", WIDTH // 2, HEIGHT // 2 + 240, exit_shop, ()),
]

def draw_shop(win):
    from main import player, draw_currency
    
    t = pygame.time.get_ticks() // 50
    t %= TILE_SIZE
    for x in range(WIDTH // TILE_SIZE + 1):
        for y in range(HEIGHT // TILE_SIZE + 1):
            if (x + y) % 2 == 0:
                pygame.draw.rect(win, '#abef70', (x * TILE_SIZE - t, y * TILE_SIZE - t, TILE_SIZE, TILE_SIZE))

    # TODO: Cards instead of buttons
    win.blit(t := big_font_render("Shop", 'black'), (WIDTH // 2 - t.get_width() // 2, 25))
    y = 85
    win.blit(t := normal_font_render(f"Carrots Sold ({item_prices[ITEM_TYPE.CARROT]}c per): {player.get_sold(ITEM_TYPE.CARROT)}", 'black'), (WIDTH // 2 - t.get_width() // 2, y))
    y += t.get_height()
    win.blit(t := normal_font_render(f"Onions Sold ({item_prices[ITEM_TYPE.ONION]}c per): {player.get_sold(ITEM_TYPE.ONION)}", 'black'), (WIDTH // 2 - t.get_width() // 2, y))
    y += t.get_height()
    win.blit(t := normal_font_render(f"Wheat Sold ({item_prices[ITEM_TYPE.WHEAT]}c per): {player.get_sold(ITEM_TYPE.WHEAT)}", 'black'), (WIDTH // 2 - t.get_width() // 2, y))
    y += t.get_height()
    win.blit(t := normal_font_render(f"Profit: {player.profit}", 'black'), (WIDTH // 2 - t.get_width() // 2, y))
    
    draw_currency()

    for b in shop_buttons:
        b.draw(win)

def shop_click(mx, my):
    for b in shop_buttons:
        b.on_click(mx, my)

def shop_hover(mx, my):
    for b in shop_buttons:
        b.on_hover(mx, my)