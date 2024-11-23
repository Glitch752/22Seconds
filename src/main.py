import graphics
from graphics import WIN, BIG_FONT, SMALL_FONT
import pygame
import constants
from constants import WIDTH, HEIGHT, TILE_SIZE
from player import Player
from map import Map

player = Player(0, 0, TILE_SIZE // 2 - 10)
map = Map()

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

def main():
    clock = pygame.time.Clock()
    delta = 0

    main_menu = True

    run = True

    while run:
        delta = clock.tick(60) / 1000

        if delta:
            pygame.display.set_caption(f"{constants.GAMENAME} | {(1 / delta):.2f}fps")

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.KEYDOWN:
                if main_menu and event.key == pygame.K_RETURN:
                    main_menu = False
        
        # GAMEPLAY
        if not main_menu:
            update_player_movement(delta)
    
        # DRAW LOOP
        WIN.fill('#bbff70')
        
        # DRAW CHECKERBOARD TILES
        if main_menu:
            draw_main_menu()
        else:
            map.update(delta)
            map.draw(WIN, player)
            player.draw(WIN)

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()