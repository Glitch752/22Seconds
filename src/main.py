from graphics import WIN, GIANT_FONT, big_font_render, SMALL_FONT, draw_all_deferred, draw_floating_hint_texts
import pygame
import constants
from constants import WIDTH, HEIGHT, TILE_SIZE, clamp
from player import Player
from map import Map, MAP_WIDTH, MAP_HEIGHT
from dialogue import DialogueManager
from day_cycle import draw_day_fading, update_day_cycle
from particle import draw_particles, update_particles
from items import ITEM_TYPE, item_prices
from ui import *
import math
import os

player = Player(MAP_WIDTH * TILE_SIZE // 2, MAP_HEIGHT * TILE_SIZE // 2, TILE_SIZE // 2 - 10)
map = Map()
dialogue = DialogueManager()

def buy_item(item):
    price = item_prices[item]

    if player.currency >= price:
        player.currency -= price

        player.items[item] += 1

class GameState:
    MainMenu = 0
    Playing = 1
    InShop = 2
game_state = GameState.MainMenu

def set_game_state(state):
    global game_state
    game_state = state

# TODO: UI interaction sounds (hover, click)

shop_buttons = [
    Button(f"Buy Carrot Seed - {item_prices[ITEM_TYPE.CARROT_SEEDS]}c", WIDTH // 2, HEIGHT // 2, buy_item, (ITEM_TYPE.CARROT_SEEDS,)),
    Button(f"Buy Onion Seed - {item_prices[ITEM_TYPE.ONION_SEEDS]}c", WIDTH // 2, HEIGHT // 2 + 40, buy_item, (ITEM_TYPE.ONION_SEEDS,)),
    Button(f"Buy Wheat Seed - {item_prices[ITEM_TYPE.WHEAT_SEEDS]}c", WIDTH // 2, HEIGHT // 2 + 80, buy_item, (ITEM_TYPE.WHEAT_SEEDS,)),
    Button(f"Buy Wall - {item_prices[ITEM_TYPE.WALL]}c", WIDTH // 2, HEIGHT // 2 + 120, buy_item, (ITEM_TYPE.WALL,)),
    Button(f"Exit Shop", WIDTH // 2, HEIGHT // 2 + 200, set_game_state, (GameState.Playing,)),
]

day_track = os.path.join("assets", "audio", "main_track.wav")
night_track = os.path.join("assets", "audio", "track2.wav")

def update_player_movement(delta):
    keys = pygame.key.get_pressed()
    movement_x = (keys[pygame.K_d] or keys[pygame.K_RIGHT]) - (keys[pygame.K_a] or keys[pygame.K_LEFT])
    movement_y = (keys[pygame.K_s] or keys[pygame.K_DOWN]) - (keys[pygame.K_w] or keys[pygame.K_UP])
    player.update(movement_x, movement_y, map, delta)

def draw_main_menu():
    t = pygame.time.get_ticks() // 50
    t %= TILE_SIZE
    for x in range(WIDTH // TILE_SIZE + 1):
        for y in range(HEIGHT // TILE_SIZE + 1):
            if (x + y) % 2 == 0:
                pygame.draw.rect(WIN, '#abef70', (x * TILE_SIZE - t, y * TILE_SIZE - t, TILE_SIZE, TILE_SIZE))

    WIN.blit(t := GIANT_FONT.render(constants.GAMENAME, True, 'black'), (WIDTH // 2 - t.get_width() // 2, HEIGHT * 0.25 - t.get_height() // 2))
    WIN.blit(t := SMALL_FONT.render("Press Enter to Play", True, 'black'), (WIDTH // 2 - t.get_width() // 2, HEIGHT * 0.75 - t.get_height() // 2))    

def draw_shop():
    t = pygame.time.get_ticks() // 50
    t %= TILE_SIZE
    for x in range(WIDTH // TILE_SIZE + 1):
        for y in range(HEIGHT // TILE_SIZE + 1):
            if (x + y) % 2 == 0:
                pygame.draw.rect(WIN, '#abef70', (x * TILE_SIZE - t, y * TILE_SIZE - t, TILE_SIZE, TILE_SIZE))

    # TODO: Cards instead of buttons
    WIN.blit(t := big_font_render("Shop", 'black'), (WIDTH // 2 - t.get_width() // 2, 25))
    y = 85
    WIN.blit(t := normal_font_render(f"Carrots Sold: {player.get_sold(ITEM_TYPE.CARROT)}", 'black'), (WIDTH // 2 - t.get_width() // 2, y))
    y += t.get_height()
    WIN.blit(t := normal_font_render(f"Onions Sold: {player.get_sold(ITEM_TYPE.ONION)}", 'black'), (WIDTH // 2 - t.get_width() // 2, y))
    y += t.get_height()
    WIN.blit(t := normal_font_render(f"Wheat Sold: {player.get_sold(ITEM_TYPE.WHEAT)}", 'black'), (WIDTH // 2 - t.get_width() // 2, y))
    y += t.get_height()
    WIN.blit(t := normal_font_render(f"Profit: {player.profit}", 'black'), (WIDTH // 2 - t.get_width() // 2, y))
    
    WIN.blit(big_font_render(f"Currency: {player.currency}c", 'black'), (7, 7))
    WIN.blit(big_font_render(f"Currency: {player.currency}c", 'yellow'), (5, 5))

    for b in shop_buttons:
        b.draw(WIN)

NON_INTERACTABLE_SELECTION_COLOR = 'yellow'
INTERACTABLE_SELECTION_COLOR = 'green'
NOTHING_SELECTION_COLOR = 'gray'

selected_cell_x = 0
selected_cell_y = 0
selection_color = NON_INTERACTABLE_SELECTION_COLOR

run = True

def handle_inputs(mx, my):
    global run, game_state, selected_cell_x, selected_cell_y, selection_color

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        elif event.type == pygame.KEYDOWN:
            if game_state == GameState.MainMenu and event.key == pygame.K_RETURN:
                set_game_state(GameState.Playing)
            if game_state == GameState.Playing and event.key == pygame.K_p:
                set_game_state(GameState.InShop)
                player.sell_items()
            if pygame.K_0 <= event.key <= pygame.K_9:
                print(event.key - pygame.K_0)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if game_state == GameState.Playing: # LMB
                    if not player.mouse_down(mx, my):
                        dialogue.on_confirm()
                elif game_state == GameState.InShop:
                    for b in shop_buttons:
                        b.on_click(mx, my)
        elif event.type == pygame.MOUSEWHEEL:
            player.update_slot_selection(event.y)
    
    if not player.over_ui(mx, my) and game_state == GameState.Playing: # This is a bit of a mess
        selected_item = player.get_selected_item()[0]
        interaction = map.get_interaction(selected_cell_x, selected_cell_y, selected_item, player)
        selection_color = INTERACTABLE_SELECTION_COLOR if interaction else NON_INTERACTABLE_SELECTION_COLOR
        
        if interaction != None and pygame.mouse.get_pressed(3)[0]:
            result = interaction()
            if result == -1:
                player.decrement_selected_item_quantity()
    else:
        selection_color = NOTHING_SELECTION_COLOR

def main():
    global run, game_state, selected_cell_x, selected_cell_y, selection_color, particles
    
    clock = pygame.time.Clock()
    delta = 0

    dialogue.queue_dialogue([
        "Harold",
        "Hello, World!",
        "I am Harold!",
        "Harold",
        "Hello, World!",
        "I am Harold!",
        "Harold",
        "Hello, World!",
        "I am Harold!",
        "Harold",
        "Hello, World!"
    ])

    dialogue.on_confirm()

    pygame.mixer.music.load(day_track)
    pygame.mixer.music.queue(night_track)

    while run:
        delta = clock.tick_busy_loop(60) / 1000 # Fixes stuttering for some reason

        if delta:
            pygame.display.set_caption(f"{constants.GAMENAME} | {(1 / delta):.2f}fps")

        mx, my = pygame.mouse.get_pos()

        if game_state == GameState.InShop:
            for b in shop_buttons:
                b.on_hover(mx, my)

        player_cell_x = player.pos.x // TILE_SIZE
        player_cell_y = player.pos.y // TILE_SIZE

        reach = 2
        selected_cell_x = math.floor(
            clamp((mx + player.pos.x - WIDTH // 2) // TILE_SIZE, player_cell_x - reach, player_cell_x + reach)
        )
        selected_cell_y = math.floor(
            clamp((my + player.pos.y - HEIGHT // 2) // TILE_SIZE, player_cell_y - reach, player_cell_y + reach)
        )

        handle_inputs(mx, my)

        # GAMEPLAY
        if game_state == GameState.Playing:
            update_particles(delta)
            update_player_movement(delta)
            dialogue.update(delta)
            update_day_cycle(delta)
    
        # DRAW LOOP
        WIN.fill("#bbff70" if game_state != GameState.Playing else "#000000")
        
        # DRAW CHECKERBOARD TILES
        if game_state == GameState.MainMenu:
            draw_main_menu()
        elif game_state == GameState.InShop:
            # TODO: Draw shop
            draw_shop()
        else:
            map.update()
            map.draw(WIN, delta, player, selected_cell_x, selected_cell_y, selection_color)
            
            draw_particles(WIN, player.pos)
            player.draw_player(WIN)
            
            draw_day_fading(WIN)
            
            draw_floating_hint_texts(WIN, player.pos)
            
            player.draw_ui(WIN)
            dialogue.draw(WIN)
        
        draw_all_deferred()

        pygame.display.flip()

    pygame.quit()