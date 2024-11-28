import pygame
import constants
from game import Game
from game_scene.playing import PlayingGameScene
from ui import *

game = Game()

def main():
    global game
    
    # game.start(IntroCutsceneScene(game))
    # TEMPORARY
    game.start(PlayingGameScene(game))
    
    clock = pygame.time.Clock()
    while not game.should_quit_game:
        current_monitor_refresh_rate = pygame.display.get_current_refresh_rate()
        delta = clock.tick_busy_loop(current_monitor_refresh_rate) / 1000 # Fixes stuttering for some reason

        if delta:
            pygame.display.set_caption(f"{constants.GAME_NAME} | {(1.0 / delta):.2f}fps")
        
        game.run(delta)

    pygame.quit()