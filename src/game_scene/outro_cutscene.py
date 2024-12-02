from typing import Self

import pygame
from game import Game
from game_scene import GameScene
from inputs import Inputs

class OutroCutsceneScene(GameScene):
    def __init__(self: Self, game: Game):
        super().__init__(game, "outro_cutscene")
        self.cutscene_text = [
            [
                "Thank you for playing."
            ],
            [
                "This game...",
                "Didn't exactly turn out how we wanted it to."
            ],
            [
                "  ",
                "We didn't have time to develop any lore",
                "or a story, so it ended up basically just being",
                "a farming simulator. If you're interested,",
                "the whole plot was _supposed_ to be centered",
                "around how our main character was a rich",
                "industrialist and the 'shadow machines'",
                "represent the damage they've done. This",
                "unfortunately didn't make it into the game."
            ],
            [
                "Regardless, we hope you enjoyed playing!",
                "We had a lot of fun making this game,",
                "and we intend to continue working on it",
                "in the future. If you have any feedback,",
                "please let us know!"
            ]
        ]
    
    def enter(self: Self):
        for box in self.cutscene_text:
            self.game.dialogue_manager.queue_dialogue(box)
    
    def draw(self: Self, win: pygame.Surface, inputs: Inputs):
        win.fill("#000000")
    
    def update(self: Self, inputs: Inputs, dt: float):
        if len(self.game.dialogue_manager.queue) == 0 and not self.game.dialogue_manager.is_shown():
            # TODO: Better ending lol
            pygame.quit()
            print("You win!")
            exit()