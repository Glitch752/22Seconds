from typing import Self

import pygame
from game import Game
from game_scene import GameScene
from inputs import Inputs

class IntroCutsceneScene(GameScene):
    def __init__(self: Self, game: Game):
        super().__init__(game, "intro_cutscene")
        self.cutscene_text = [
            [
                "You",
                "This is a test message that doesn't mean anything.",
            ],
            [
                "Doctor",
                "I see. And how does that make you feel?",
            ],
            [
                "You",
                "I don't exist. I'm a figment of your imagination.",
            ],
            [
                "Doctor",
                "Does that...",
                "Mean I don't exist either?",
            ],
            [
                "Wow",
                "So deep."
            ]
        ]
    
    def enter(self: Self):
        for box in self.cutscene_text:
            self.game.dialogue_manager.queue_dialogue(box)
    
    def draw(self: Self, win: pygame.Surface, inputs: Inputs):
        win.fill("#000000")
    
    def update(self: Self, inputs: Inputs, dt: float):
        if len(self.game.dialogue_manager.queue) == 0 and not self.game.dialogue_manager.is_shown():
            self.game.enter_playing_scene()