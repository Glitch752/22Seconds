from typing import Self

import pygame
from constants import HEIGHT, TILE_SIZE, WIDTH
import constants
from game import Game
from game_scene import GameScene, IntroCutsceneScene
from graphics import GIANT_FONT, SMALL_FONT
from inputs import InputType

class MainMenuScene(GameScene):
    def __init__(self: Self, game: Game):
        super().__init__(game)
    
    def enter(self: Self):
        self.game.music.play_day_track()
    
    def draw(self: Self, win: pygame.Surface):
        win.fill("#bbff70")
        
        t = pygame.time.get_ticks() // 50
        t %= TILE_SIZE
        for x in range(WIDTH // TILE_SIZE + 1):
            for y in range(HEIGHT // TILE_SIZE + 1):
                if (x + y) % 2 == 0:
                    pygame.draw.rect(win, '#abef70', (x * TILE_SIZE - t, y * TILE_SIZE - t, TILE_SIZE, TILE_SIZE))

        win.blit(t := GIANT_FONT.render(constants.GAME_NAME, True, 'black'), (2 + WIDTH // 2 - t.get_width() // 2, 2 + HEIGHT * 0.25 - t.get_height() // 2))
        win.blit(t := GIANT_FONT.render(constants.GAME_NAME, True, 'white'), (WIDTH // 2 - t.get_width() // 2, HEIGHT * 0.25 - t.get_height() // 2))
        win.blit(t := SMALL_FONT.render("Press Enter to Play", True, 'black'), (1 + WIDTH // 2 - t.get_width() // 2, 1 + HEIGHT * 0.75 - t.get_height() // 2))    
        win.blit(t := SMALL_FONT.render("Press Enter to Play", True, 'white'), (WIDTH // 2 - t.get_width() // 2, HEIGHT * 0.75 - t.get_height() // 2))    
        win.blit(t := SMALL_FONT.render("Made by Brody, Mikey, and Elly", True, 'black'), (1 + WIDTH // 2 - t.get_width() // 2, 1 + HEIGHT * 0.9 - t.get_height() // 2))    
        win.blit(t := SMALL_FONT.render("Made by Brody, Mikey, and Elly", True, 'white'), (WIDTH // 2 - t.get_width() // 2, HEIGHT * 0.9 - t.get_height() // 2))    
    
    def event_input(self: Self, _type: InputType):
        # No matter what, we switch to the intro cutscene
        self.game.update_scene(IntroCutsceneScene(self.game))