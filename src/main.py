import pygame
import constants
from game import Game
from game_scene.intro_cutscene import IntroCutsceneScene
from ui import *

game = Game()

def main():
    global game
    
    game.start(IntroCutsceneScene(game))
    
    clock = pygame.time.Clock()
    while not game.should_quit_game:
        delta = clock.tick_busy_loop(0) / 1000 # Fixes stuttering for some reason

        if delta:
            pygame.display.set_caption(f"{constants.GAME_NAME} | {(1 / delta):.2f}fps")
        
        game.run(delta)

    pygame.quit()