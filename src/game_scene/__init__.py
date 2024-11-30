from abc import ABC, abstractmethod
from typing import Self
import pygame

from typing import TYPE_CHECKING

from graphics import get_height, get_width
if TYPE_CHECKING:
    from game import Game

from inputs import InputType, Inputs

class GameScene(ABC):
    """
    A game scene.
    Game scenes can store state, but they are usually instantiated every time they are entered in our case.  
    The exception is PlayingGameScene, which is instantiated once and reused throughout the game.
    """
    
    name: str
    
    def __init__(self: Self, game: "Game", name: str):
        self.game = game
        self.name = name

    def update(self: Self, inputs: Inputs, dt: float):
        pass

    @abstractmethod # Must be implemented
    def draw(self: Self, win: pygame.Surface, inputs: Inputs):
        pass
    
    def event_input(self: Self, type: InputType):
        pass

    def enter(self: Self):
        pass

    def exit(self: Self):
        pass
    
    def get_target_reference(self: Self) -> pygame.Vector2:
        return pygame.Vector2(get_width() // 2, get_height() // 2)