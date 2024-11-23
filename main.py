from constants import *

def main():
    clock = pygame.time.Clock()
    delta = 0

    main_menu = True

    run = True

    while run:
        delta = clock.tick(30) / 1000

        if delta:
            pygame.display.set_caption(f"{GAMENAME} | {(1 / delta):.2f}fps")

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.KEYDOWN:
                if main_menu and event.key == pygame.K_RETURN:
                    main_menu = False
    
        WIN.fill('#bbff70')

        for x in range(WIDTH // TILE_SIZE):
            for y in range(HEIGHT // TILE_SIZE):
                if (x + y) % 2 == 0:
                    pygame.draw.rect(WIN, '#abef70', (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))

        if main_menu:
            WIN.blit(t := BIG_FONT.render(GAMENAME, True, 'black'), (WIDTH // 2 - t.get_width() // 2, HEIGHT * 0.25 - t.get_height() // 2))
            WIN.blit(t := SMALL_FONT.render("Press Enter to Play", True, 'black'), (WIDTH // 2 - t.get_width() // 2, HEIGHT * 0.75 - t.get_height() // 2))

        pygame.display.flip()

    pygame.quit()

main()