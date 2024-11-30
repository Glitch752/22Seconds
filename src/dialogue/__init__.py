from abc import ABC, abstractmethod
from enum import StrEnum
import pygame
from audio import AudioManager
from dialogue.renderer import DialogueRenderer

class WorldEvent(StrEnum):
    GameStart = "game_start"
    DrWhomShopkeeper = "dr_whom_shopkeeper"
    AfterFirstShopInteraction = "after_first_shop_interaction"

class ConditionState:
    # Maps WorldEvent to the time it was triggered
    world_events: dict[WorldEvent, int | None]

    def __init__(self) -> None:
        self.world_events = {}
    
    def add_event(self, event: WorldEvent):
        self.world_events[event] = pygame.time.get_ticks()
    
    def time_since_event(self, event: WorldEvent) -> int | None:
        if event not in self.world_events or self.world_events[event] == None:
            return None
        return pygame.time.get_ticks() - self.world_events[event]

class DialogueCondition(ABC):
    @abstractmethod
    def check(self, condition_state: ConditionState) -> bool:
        pass

class AndCondition(DialogueCondition):
    conditions: list[DialogueCondition]

    def __init__(self, conditions: list[DialogueCondition]) -> None:
        self.conditions = conditions

    def check(self, condition_state: ConditionState) -> bool:
        return all(c.check() for c in self.conditions)

class OrCondition(DialogueCondition):
    conditions: list[DialogueCondition]

    def __init__(self, conditions: list[DialogueCondition]) -> None:
        self.conditions = conditions

    def check(self, condition_state: ConditionState) -> bool:
        return any(c.check() for c in self.conditions)

class BeforeEventCondition(DialogueCondition):
    event: WorldEvent

    def __init__(self, event: WorldEvent) -> None:
        self.event = event

    def check(self, condition_state: ConditionState) -> bool:
        return not condition_state.has_event(self.event)

class AfterEventCondition(DialogueCondition):
    event: WorldEvent
    elapsed_time: int

    def __init__(self, event: WorldEvent, elapsed_time: int = 0) -> None:
        self.event = event
        self.elapsed_time = elapsed_time

    def check(self, condition_state: ConditionState) -> bool:
        return condition_state.time_since_event(self.event) != None and condition_state.time_since_event(self.event) >= self.elapsed_time

class DialogueManager:
    renderer: DialogueRenderer = DialogueRenderer()
    
    queue: list[list[str]] = []
    current_lines: list[str] = []

    def queue_dialogue(self, lines: list[str]):
        self.queue.append(lines)
    
    def on_confirm(self):
        if self.is_active():
            self.done = True
            self.renderer.skip_to_end(self.current_lines)
        else:
            self.current_lines.clear()
            self.renderer.reset()
            if len(self.queue):
                self.current_lines = self.queue.pop(0)
    
    def is_shown(self):
        return len(self.current_lines) != 0
    
    def is_active(self):
        return len(self.current_lines) != 0 and not self.renderer.done
    
    def update(self, delta: float, audio_manager: AudioManager):
        if not self.is_active():
            return
        
        self.renderer.update(self.current_lines, delta, audio_manager)
    
    def draw(self, win: pygame.Surface):
        if len(self.current_lines):
            self.renderer.draw(win, self.current_lines)