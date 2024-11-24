import random
from graphics import WIN, BIG_FONT, SMALL_FONT, draw_all_deferred, draw_floating_hint_texts
import pygame
import constants
from constants import WIDTH, HEIGHT, TILE_SIZE, clamp
from player import Player
from map import Map, MAP_WIDTH, MAP_HEIGHT, TILE_TYPE
import math
from dialogue import DialogueManager
from day_cycle import draw_day_fading, update_day_cycle, get_brightness
from particle import Particle

player = Player(MAP_WIDTH * TILE_SIZE // 2, MAP_HEIGHT * TILE_SIZE // 2, TILE_SIZE // 2 - 10)
map = Map()
dialogue = DialogueManager()
particles: list[Particle] = []

def update_player_movement(delta):
    keys = pygame.key.get_pressed()
    movement_x = (keys[pygame.K_d] or keys[pygame.K_RIGHT]) - (keys[pygame.K_a] or keys[pygame.K_LEFT])
    movement_y = (keys[pygame.K_s] or keys[pygame.K_DOWN]) - (keys[pygame.K_w] or keys[pygame.K_UP])
    player.update(movement_x, movement_y, delta)

def draw_main_menu():
    t = pygame.time.get_ticks() // 50
    t %= TILE_SIZE
    for x in range(WIDTH // TILE_SIZE + 1):
        for y in range(HEIGHT // TILE_SIZE + 1):
            if (x + y) % 2 == 0:
                pygame.draw.rect(WIN, '#abef70', (x * TILE_SIZE - t, y * TILE_SIZE - t, TILE_SIZE, TILE_SIZE))

    WIN.blit(t := BIG_FONT.render(constants.GAMENAME, True, 'black'), (WIDTH // 2 - t.get_width() // 2, HEIGHT * 0.25 - t.get_height() // 2))
    WIN.blit(t := SMALL_FONT.render("Press Enter to Play", True, 'black'), (WIDTH // 2 - t.get_width() // 2, HEIGHT * 0.75 - t.get_height() // 2))    

NON_INTERACTABLE_SELECTION_COLOR = 'yellow'
INTERACTABLE_SELECTION_COLOR = 'green'
NOTHING_SELECTION_COLOR = 'gray'

selected_cell_x = 0
selected_cell_y = 0
selection_color = NON_INTERACTABLE_SELECTION_COLOR
main_menu = True
run = True

def handle_inputs(mx, my):
    global run, main_menu, selected_cell_x, selected_cell_y, selection_color

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        elif event.type == pygame.KEYDOWN:
            if main_menu and event.key == pygame.K_RETURN:
                main_menu = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and not main_menu: # LMB
                if not player.mouse_down(mx, my):
                    dialogue.on_confirm()
        elif event.type == pygame.MOUSEWHEEL:
            player.update_slot_selection(event.y)
    
    if not player.over_ui(mx, my) and not main_menu: # This is a bit of a mess
        selected_item = player.get_selected_item()[0]
        interaction = map.get_interaction(selected_cell_x, selected_cell_y, selected_item)
        selection_color = INTERACTABLE_SELECTION_COLOR if interaction else NON_INTERACTABLE_SELECTION_COLOR
        
        if interaction != None and pygame.mouse.get_pressed(3)[0]:
            result = interaction()
            if result == -1:
                player.decrement_selected_item_quantity()
    else:
        selection_color = NOTHING_SELECTION_COLOR

def main():
    global run, main_menu, selected_cell_x, selected_cell_y, selection_color, particles
    
    clock = pygame.time.Clock()
    delta = 0

    dialogue.queue_dialogue([
        "Harold",
        "Hello, World!",
        "I am Harold!"
    ])

    dialogue.queue_dialogue([
        "Gerald",
        "Fuck you, Harold!",
    ])
    dialogue.on_confirm()

    while run:
        delta = clock.tick_busy_loop(60) / 1000 # Fixes stuttering for some reason

        if delta:
            pygame.display.set_caption(f"{constants.GAMENAME} | {(1 / delta):.2f}fps")

        mx, my = pygame.mouse.get_pos()

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
        if not main_menu:
            for p in particles[::-1]:
                p.update(delta)

                if p.done:
                    particles.remove(p)
            
            update_player_movement(delta)
            dialogue.update(delta)
            update_day_cycle(delta)
    
        # DRAW LOOP
        WIN.fill("#bbff70" if main_menu else "#000000")
        
        # DRAW CHECKERBOARD TILES
        if main_menu:
            draw_main_menu()
        else:
            map.update(delta, particles)
            map.draw(WIN, player, selected_cell_x, selected_cell_y, selection_color)
            player.draw_player(WIN)
            
            for p in particles:
                p.draw(WIN, player.pos)
            
            draw_day_fading(WIN)
            
            player.draw_ui(WIN)
            
            dialogue.draw(WIN)
            draw_floating_hint_texts(WIN, player.pos)
        
        draw_all_deferred()

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()