from abc import ABC, abstractmethod
from typing import Self
import pygame

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from game import Game

from inputs import InputType, Inputs

class GameScene(ABC):
    """
    A game scene.
    Game scenes can store state, but they are usually instantiated every time they are entered in our case.  
    The exception is PlayingGameScene, which is instantiated once and reused throughout the game.
    """
    
    def __init__(self: Self, game: "Game"):
        self.game = game

    def update(self: Self, inputs: Inputs, dt: float):
        pass

    @abstractmethod # Must be implemented
    def draw(self: Self, win: pygame.Surface):
        pass
    
    def event_input(self: Self, type: InputType):
        pass

    def enter(self: Self):
        pass

    def exit(self: Self):
        pass