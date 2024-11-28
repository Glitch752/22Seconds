from typing import Self

import pygame
from game import Game
from game_scene import GameScene, PlayingGameScene
from inputs import Inputs

class OutroCutsceneScene(GameScene):
    def __init__(self: Self, game: Game):
        super().__init__(game)
        self.cutscene_text = [
            [
                "Well, this is it..."
            ],
            [
                "You win.",
                "It's over now."
            ],
            [
                "...",
                "And how does that make you feel?"
                # Wow such dialogue
            ]
        ]
    
    def enter(self: Self):
        for box in self.cutscene_text:
            self.game.dialogue.queue_dialogue(box)
        self.game.dialogue.on_confirm()
    
    def draw(self: Self, win: pygame.Surface):
        win.fill("#000000")
    
    def update(self: Self, inputs: Inputs, dt: float):
        if len(self.game.dialogue.queue) == 0 and not self.game.dialogue.is_shown():
            # TODO: Better ending lol
            pygame.quit()
            print("You win!")
            exit()