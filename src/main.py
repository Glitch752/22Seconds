from graphics import WIN, GIANT_FONT, big_font_render, SMALL_FONT, draw_all_deferred, draw_floating_hint_texts
import pygame
import constants
from constants import WIDTH, HEIGHT, TILE_SIZE, clamp
from player import Player
from map import Map, MAP_WIDTH, MAP_HEIGHT
from dialogue import DialogueManager
from day_cycle import draw_day_fading, play_sounds, update_day_cycle, get_formatted_time
from particle import draw_particles, update_particles
from items import ITEM_TYPE, item_prices
from ui import *
import math
import os

player = Player(MAP_WIDTH * TILE_SIZE // 2, MAP_HEIGHT * TILE_SIZE // 2, TILE_SIZE // 2 - 10)
map = Map()
dialogue = DialogueManager()

buy_item_sound = pygame.mixer.Sound(os.path.join("assets", "audio", "chaChing.wav")) # TODO: Better purchase sound
eurgh_item_sound = pygame.mixer.Sound(os.path.join("assets", "audio", "Aeeaahghgh.wav")) # TODO: Better bad eurgh sound

def buy_item(item, received_quantity=1):
    price = item_prices[item]

    if player.currency >= price:
        player.currency -= price

        player.items[item] += received_quantity
        
        buy_item_sound.play()
    else:
        eurgh_item_sound.play()

def try_to_win_lmao():
    if player.currency >= 1000:
        set_game_state(GameState.Cutscene_Outro)
    else:
        eurgh_item_sound.play()

class GameState:
    MainMenu = 0
    Playing = 1
    InShop = 2
    Cutscene_Intro = 3
    Cutscene_Outro = 4
game_state = GameState.MainMenu

def set_game_state(state):
    global game_state
    game_state = state

# TODO: UI interaction sounds (hover, click)

day_track = os.path.join("assets", "audio", "main_track.wav")
night_track = os.path.join("assets", "audio", "track2.wav")
shop_track = os.path.join("assets", "audio", "track3.wav")

def exit_shop():
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
    WIN.blit(t := SMALL_FONT.render("Made by Brody, Mikey, and Elly", True, 'black'), (WIDTH // 2 - t.get_width() // 2, HEIGHT * 0.9 - t.get_height() // 2))    

def draw_currency():
    WIN.blit(big_font_render(f"Currency: {player.currency}c", 'black'), (17, 17))
    WIN.blit(big_font_render(f"Currency: {player.currency}c", 'yellow'), (15, 15))
def draw_time():
    time = get_formatted_time()
    WIN.blit(surface := big_font_render(time, 'black'), (17, HEIGHT - 15 - surface.get_height()))
    WIN.blit(surface := big_font_render(time, 'green'), (15, HEIGHT - 17 - surface.get_height()))

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
    WIN.blit(t := normal_font_render(f"Carrots Sold ({item_prices[ITEM_TYPE.CARROT]}c per): {player.get_sold(ITEM_TYPE.CARROT)}", 'black'), (WIDTH // 2 - t.get_width() // 2, y))
    y += t.get_height()
    WIN.blit(t := normal_font_render(f"Onions Sold ({item_prices[ITEM_TYPE.ONION]}c per): {player.get_sold(ITEM_TYPE.ONION)}", 'black'), (WIDTH // 2 - t.get_width() // 2, y))
    y += t.get_height()
    WIN.blit(t := normal_font_render(f"Wheat Sold ({item_prices[ITEM_TYPE.WHEAT]}c per): {player.get_sold(ITEM_TYPE.WHEAT)}", 'black'), (WIDTH // 2 - t.get_width() // 2, y))
    y += t.get_height()
    WIN.blit(t := normal_font_render(f"Profit: {player.profit}", 'black'), (WIDTH // 2 - t.get_width() // 2, y))
    
    draw_currency()

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
            if dialogue.is_shown():
                dialogue.on_confirm()
            elif game_state == GameState.MainMenu and event.key == pygame.K_RETURN:
                set_game_state(GameState.Cutscene_Intro)
            elif game_state == GameState.Playing and event.key == pygame.K_p:
                set_game_state(GameState.InShop)
                player.sell_items()
            elif pygame.K_0 <= event.key <= pygame.K_9:
                player_slots = len(player.get_interactable_items())
                slot = max(1, min(player_slots, event.key - pygame.K_0))
                player.select_slot(player_slots - slot)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if game_state == GameState.Playing: # LMB
                    player.mouse_down(mx, my)
                elif game_state == GameState.InShop:
                    for b in shop_buttons:
                        b.on_click(mx, my)
        elif event.type == pygame.MOUSEWHEEL:
            player.update_slot_selection(event.y)
    
    if not player.over_ui(mx, my) and game_state == GameState.Playing: # This is a bit of a mess
        selected_item = player.get_selected_item()[0]
        interaction = map.get_interaction(selected_cell_x, selected_cell_y, selected_item, player)
        selection_color = INTERACTABLE_SELECTION_COLOR if interaction else NON_INTERACTABLE_SELECTION_COLOR

        if interaction != None:
            if pygame.mouse.get_pressed(3)[0]:
                if not player.wait_for_mouseup:
                    result = interaction()
                    if result == -1:
                        player.decrement_selected_item_quantity()
            else:
                player.wait_for_mouseup = False
    else:
        selection_color = NOTHING_SELECTION_COLOR

def main():
    global run, game_state, selected_cell_x, selected_cell_y, selection_color, particles
    
    clock = pygame.time.Clock()
    delta = 0

    dialogue.on_confirm()

    pygame.mixer.music.load(day_track)
    pygame.mixer.music.play()
    
    last_game_state = game_state

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
        play_sounds()

        # GAMEPLAY
        if game_state == GameState.Playing:
            update_particles(delta)
            update_player_movement(delta)
            update_day_cycle(delta, player)
    
        dialogue.update(delta)
        
        # DRAW LOOP
        WIN.fill("#bbff70" if game_state in [GameState.MainMenu, GameState.InShop] else "#000000")
        
        just_changed_state = last_game_state != game_state
        last_game_state = game_state
        
        # DRAW CHECKERBOARD TILES
        if game_state == GameState.MainMenu:
            draw_main_menu()
        elif game_state == GameState.InShop:
            # TODO: Draw shop
            draw_shop()
        elif game_state == GameState.Cutscene_Intro:
            if just_changed_state:  
                intro_cutscene_text = [
                    [
                        "You",
                        "I think it was like, 1 in the morning.",
                        "I woke up the whole house...",
                        "    screamed my lungs out...",
                        "I don't know what to do anymore...",
                    ],
                    [
                        "Doctor",
                        "Mhm... Has it been just the screaming,",
                        "or have you been experiencing any other symptoms?",
                        "Shortness of breath, rashing, anything like that?",
                    ],
                    [
                        "You",
                        "I guess... there's the dread.",
                        "    Every night, I go to sleep terrified.",
                        "    It's like... something is going to happen.",
                        "And when I wake up, usually it's nothing... but...",
                    ],
                    [
                        "Doctor",
                        "Mhm?",
                    ],
                    [
                        "You",
                        "Recently, there's been some... thing...",
                        "getting into my farm.",
                        "It destroys almost everything I have..."
                    ],
                    [
                        "You",
                        "Oh, well... I guess I should get going.",
                    ],
                    [
                        "Doctor",
                        "Wait-",
                    ],
                ]
                for box in intro_cutscene_text:
                    dialogue.queue_dialogue(box)
                dialogue.on_confirm()
            elif len(dialogue.queue) == 0 and not dialogue.is_shown():
                set_game_state(GameState.Playing)
        elif game_state == GameState.Cutscene_Outro:
            if just_changed_state:  
                intro_cutscene_text = [
                    ["Doctor", "How have the symptoms been? Better?"],
                    ["You", "I haven't had the nightmares… or the screaming."],
                    ["Doctor", "And the dread?"],
                    ["You", "The dread is still there.", "It's been getting worse, if anything…"],
                    ["Doctor", "I see. In that case, we should be", "safe to increase the dosage of your medicine."],
                ]
                for box in intro_cutscene_text:
                    dialogue.queue_dialogue(box)
                dialogue.on_confirm()
            elif len(dialogue.queue) == 0 and not dialogue.is_shown():
                pygame.quit()
                print("You win!")
                exit()
        else:
            map.update()
            map.draw(WIN, delta, player, selected_cell_x, selected_cell_y, selection_color)
            
            draw_particles(WIN, player.pos)
            player.draw_player(WIN)
            
            draw_day_fading(WIN)
            
            draw_floating_hint_texts(WIN, player.pos)
            
            player.draw_ui(WIN)
            
            draw_currency()
            draw_time()
        
        dialogue.draw(WIN)
        
        draw_all_deferred()

        pygame.display.flip()

    pygame.quit()