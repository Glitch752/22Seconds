"""
Okay... I might have got a bit carried away and dramatically over-engineered this dialogue system.
It's not even really a dialogue system anymore; it's a game event scheduler. This should probably be
split into a different file or renamed to something more appropriate. I'll leave that for later.
"""

from abc import ABC, abstractmethod
from enum import StrEnum
from typing import Callable, TYPE_CHECKING
import pygame
from audio import AudioManager
from constants import ITEM_SLOT_ITEM_SIZE, ITEM_SLOT_MARGIN, ITEM_SLOT_PADDING, MAP_HEIGHT, MAP_WIDTH, TILE_SIZE
from dialogue.renderer import DialogueRenderer
from graphics import get_height, get_width
from graphics.floating_hint_text import FloatingHintText, add_floating_text_hint
from items import Item
from utils import get_username

if TYPE_CHECKING:
    from player import Player

class WorldEvent(StrEnum):
    """
    World events are essentially flags that can be set to trigger dialogue or other events.
    Some of them are cleared after being triggered, and others are persistent.
    """
    # "Game stage"-related events
    GameStart = "game_start"
    DrWhomShopkeeper = "dr_whom_shopkeeper"
    AfterFirstShopInteraction = "after_first_shop_interaction"
    StartFarming = "start_farming"
    ScaryNightsStarted = "scary_nights_started"
    FirstScaryNightStart = "first_night_start"
    FirstScaryNightEnd = "first_night_end"
    SellFirstProducePrompt = "sell_first_produce_prompt"
    
    # Tutorial-related events
    ShovelHintDone = "shovel_hint_done"
    TillHintDone = "till_hint_done"
    SeedsHintDone = "seeds_hint_done"
    
    FullyGrownPlant = "fully_grown_plant"
    HarvestHintDone = "harvest_hint_done"
    
    # Dialogue interaction events
    DialogueDrWhom = "dialogue_dr_whom"
    DialogueMrShopkeeper = "dialogue_mr_shopkeeper"

class ConditionState:
    # Maps WorldEvent to the time it was triggered
    world_events: dict[WorldEvent, int | None]
    def __init__(self) -> None:
        self.world_events = {}
        self.game_messages = set()
    
    def add_event(self, event: WorldEvent):
        self.world_events[event] = pygame.time.get_ticks()
    def clear_event(self, event: WorldEvent):
        self.world_events[event] = None
    def has_event(self, event: WorldEvent) -> bool:
        return event in self.world_events and self.world_events[event] != None
    
    def time_since_event(self, event: WorldEvent) -> int | None:
        if event not in self.world_events or self.world_events[event] == None:
            return None
        return pygame.time.get_ticks() - self.world_events[event]

# Conditions

class DialogueCondition(ABC):
    @abstractmethod
    def check(self, condition_state: ConditionState) -> bool:
        pass

class AndCondition(DialogueCondition):
    conditions: list[DialogueCondition]

    def __init__(self, *conditions: list[DialogueCondition]) -> None:
        self.conditions = conditions

    def check(self, condition_state: ConditionState) -> bool:
        return all(c.check(condition_state) for c in self.conditions)

class OrCondition(DialogueCondition):
    conditions: list[DialogueCondition]

    def __init__(self, *conditions: list[DialogueCondition]) -> None:
        self.conditions = conditions

    def check(self, condition_state: ConditionState) -> bool:
        return any(c.check(condition_state) for c in self.conditions)

class BeforeEventCondition(DialogueCondition):
    event: WorldEvent

    def __init__(self, event: WorldEvent) -> None:
        self.event = event

    def check(self, condition_state: ConditionState) -> bool:
        return condition_state.time_since_event(self.event) == None

class AfterEventCondition(DialogueCondition):
    event: WorldEvent
    elapsed_time: int

    def __init__(self, event: WorldEvent, elapsed_ms: int = 0) -> None:
        self.event = event
        self.elapsed_time = elapsed_ms

    def check(self, condition_state: ConditionState) -> bool:
        return condition_state.time_since_event(self.event) != None and condition_state.time_since_event(self.event) >= self.elapsed_time

class NotCondition(DialogueCondition):
    condition: DialogueCondition

    def __init__(self, condition: DialogueCondition) -> None:
        self.condition = condition

    def check(self, condition_state: ConditionState) -> bool:
        return not self.condition.check(condition_state)

class AlwaysCondition(DialogueCondition):
    def check(self, condition_state: ConditionState) -> bool:
        return True
class NeverCondition(DialogueCondition):
    def check(self, condition_state: ConditionState) -> bool:
        return False

class LambdaCondition(DialogueCondition):
    func: Callable[[ConditionState], bool]

    def __init__(self, func: Callable[[ConditionState], bool]) -> None:
        self.func = func

    def check(self, condition_state: ConditionState) -> bool:
        return self.func(condition_state)

# Actions

class DialogueActionContext:
    dialogue_manager: "DialogueManager"
    audio_manager: "AudioManager"
    player: "Player"
    """
    The list of queued game actions. These are currently just scene names to switch to.
    This could be an enum... or we could restructure this to not need it at all... but I'm
    lazy and don't have enough time to mess with refactors.
    """
    queued_game_actions: list[str]
    def __init__(self, dialogue_manager: "DialogueManager", audio_manager: "AudioManager", player: "Player"):
        self.dialogue_manager = dialogue_manager
        self.audio_manager = audio_manager
        self.player = player
        self.queued_game_actions = []

class DialogueAction(ABC):
    def start(self, action_context: DialogueActionContext) -> None:
        pass
    def update(self, action_context: DialogueActionContext, delta: float) -> None:
        pass
    def end(self, action_context: DialogueActionContext) -> None:
        pass
    def is_finished(self, action_context: DialogueActionContext) -> bool:
        return True

class ParallelAction(DialogueAction):
    actions: list[DialogueAction]
    def __init__(self, *actions: list[DialogueAction]) -> None:
        self.actions = actions
    def start(self, action_context: DialogueActionContext) -> None:
        for action in self.actions:
            action.start(action_context)
    def update(self, action_context: DialogueActionContext, delta: float) -> None:
        for action in self.actions:
            action.update(action_context, delta)
    def end(self, action_context: DialogueActionContext) -> None:
        for action in self.actions:
            action.end(action_context)
    def is_finished(self, action_context: DialogueActionContext) -> bool:
        return all(action.is_finished(action_context) for action in self.actions)

class SequenceAction(DialogueAction):
    actions: list[DialogueAction]
    current_action: int = 0
    def __init__(self, *actions: list[DialogueAction]) -> None:
        self.actions = actions
    def start(self, action_context: DialogueActionContext) -> None:
        self.current_action = 0
        self.actions[self.current_action].start(action_context)
    def update(self, action_context: DialogueActionContext, delta: float) -> None:
        if self.current_action < len(self.actions):
            self.actions[self.current_action].update(action_context, delta)
            
            if self.actions[self.current_action].is_finished(action_context):
                self.actions[self.current_action].end(action_context)
                self.current_action += 1
                if self.current_action < len(self.actions):
                    self.actions[self.current_action].start(action_context)
    def end(self, action_context: DialogueActionContext) -> None:
        if self.current_action < len(self.actions):
            self.actions[self.current_action].end(action_context)
    def is_finished(self, action_context: DialogueActionContext) -> bool:
        return self.current_action == len(self.actions)

class RaceAction(DialogueAction):
    actions: list[DialogueAction]
    def __init__(self, *actions: list[DialogueAction]) -> None:
        self.actions = actions
    def start(self, action_context: DialogueActionContext) -> None:
        for action in self.actions:
            action.start(action_context)
    def update(self, action_context: DialogueActionContext, delta: float) -> None:
        for action in self.actions:
            action.update(action_context, delta)
    def end(self, action_context: DialogueActionContext) -> None:
        for action in self.actions:
            action.end(action_context)
    def is_finished(self, action_context: DialogueActionContext) -> bool:
        return any(action.is_finished(action_context) for action in self.actions)

class ConditionalAction(DialogueAction):
    condition: DialogueCondition
    action: DialogueAction
    running: bool = False
    def __init__(self, condition: DialogueCondition, action: DialogueAction) -> None:
        self.condition = condition
        self.action = action
    def start(self, action_context: DialogueActionContext) -> None:
        self.running = self.condition.check(action_context.dialogue_manager.condition_state)
        if self.running:
            self.action.start(action_context)
    def update(self, action_context: DialogueActionContext, delta: float) -> None:
        if self.running:
            self.action.update(action_context, delta)
    def end(self, action_context: DialogueActionContext) -> None:
        if self.running:
            self.action.end(action_context)
    def is_finished(self, action_context: DialogueActionContext) -> bool:
        return not self.running or self.action.is_finished(action_context)

class RepeatAction(DialogueAction):
    action: DialogueAction
    times: int
    current_time: int = 0
    def __init__(self, action: DialogueAction, times: int) -> None:
        self.action = action
        self.times = times
    def start(self, action_context: DialogueActionContext) -> None:
        self.current_time = 0
        self.action.start(action_context)
    def update(self, action_context: DialogueActionContext, delta: float) -> None:
        self.action.update(action_context, delta)
        if self.action.is_finished(action_context):
            self.action.end(action_context)
            self.current_time += 1
            if self.current_time < self.times:
                self.action.start(action_context)
    def end(self, action_context: DialogueActionContext) -> None:
        self.action.end(action_context)
    def is_finished(self, action_context: DialogueActionContext) -> bool:
        return self.current_time >= self.times

class RepeatWhileAction(DialogueAction):
    action: DialogueAction
    condition: DialogueCondition
    def __init__(self, action: DialogueAction, condition: DialogueCondition) -> None:
        self.action = action
        self.condition = condition
    def start(self, action_context: DialogueActionContext) -> None:
        self.action.start(action_context)
    def update(self, action_context: DialogueActionContext, delta: float) -> None:
        self.action.update(action_context, delta)
        if self.condition.check(action_context.dialogue_manager.condition_state):
            self.action.end(action_context)
            self.action.start(action_context)
    def end(self, action_context: DialogueActionContext) -> None:
        self.action.end(action_context)
    def is_finished(self, action_context: DialogueActionContext) -> bool:
        return not self.condition.check(action_context.dialogue_manager.condition_state)

class WaitAction(DialogueAction):
    time: float
    current_time: float = 0
    def __init__(self, seconds: float) -> None:
        self.time = seconds
    def start(self, action_context: DialogueActionContext) -> None:
        self.current_time = 0
    def update(self, action_context: DialogueActionContext, delta: float) -> None:
        self.current_time += delta
    def is_finished(self, action_context: DialogueActionContext) -> bool:
        return self.current_time >= self.time

class ConditionalWaitAction(DialogueAction):
    condition: DialogueCondition
    def __init__(self, condition: DialogueCondition) -> None:
        self.condition = condition
    def is_finished(self, action_context: DialogueActionContext) -> bool:
        return self.condition.check(action_context.dialogue_manager.condition_state)

class SetEventAction(DialogueAction):
    event: WorldEvent
    def __init__(self, event: WorldEvent) -> None:
        self.event = event
    def start(self, action_context: DialogueActionContext) -> None:
        action_context.dialogue_manager.condition_state.add_event(self.event)

class ClearEventAction(DialogueAction):
    event: WorldEvent
    def __init__(self, event: WorldEvent) -> None:
        self.event = event
    def start(self, action_context: DialogueActionContext) -> None:
        action_context.dialogue_manager.condition_state.clear_event(self.event)

class LambdaAction(DialogueAction):
    func: Callable[["DialogueActionContext"], None]
    def __init__(self, func: Callable[["DialogueActionContext"], None]) -> None:
        self.func = func
    def start(self, action_context: DialogueActionContext) -> None:
        self.func(action_context)

class QueueLinesAndWaitAction(DialogueAction):
    lines: list[str]
    def __init__(self, *lines: list[str]) -> None:
        self.lines = list(lines)
    def start(self, action_context: DialogueActionContext) -> None:
        action_context.dialogue_manager.queue_dialogue(self.lines)
    def is_finished(self, action_context: DialogueActionContext) -> bool:
        return not action_context.dialogue_manager.is_shown()

class QueueGameActionAction(DialogueAction):
    action: str
    def __init__(self, scene: str) -> None:
        self.action = scene
    def start(self, action_context: DialogueActionContext) -> None:
        action_context.queued_game_actions.append(self.action)

class PrintConsoleAction(DialogueAction):
    text: str
    def __init__(self, text: str) -> None:
        self.text = text
    def start(self, action_context: DialogueActionContext) -> None:
        print(self.text)

class PlaySoundAction(DialogueAction):
    sound: str
    def __init__(self, sound: str) -> None:
        self.sound = sound
    def start(self, action_context: DialogueActionContext) -> None:
        action_context.audio_manager.play_sound(self.sound)

class GiveItemsAction(DialogueAction):
    items: tuple[tuple[Item, int]]
    def __init__(self, items: tuple[tuple[Item, int]]) -> None:
        self.items = items
    def start(self, action_context: DialogueActionContext) -> None:
        items = action_context.player.items
        offset = 0
        for item, quantity in self.items:
            if item in items:
                items[item] += quantity
            else:
                items[item] = quantity
            add_floating_text_hint(FloatingHintText(
                f"Received {quantity} {item.item_name}",
                (get_width() - 20, get_height() - ITEM_SLOT_ITEM_SIZE - ITEM_SLOT_PADDING*2 - ITEM_SLOT_MARGIN*2 - 30 - offset),
                "green", -5, 1.5, 0.25,
                fixed_in_world=False,
                alignment="right"
            ))
            offset += 25

class SetPlayerPositionAction(DialogueAction):
    x: float
    y: float
    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y
    def start(self, action_context: DialogueActionContext) -> None:
        action_context.player.pos.x = self.x
        action_context.player.pos.y = self.y

class ForcePlayerWalkAction(DialogueAction):
    x: float
    y: float
    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y
    def start(self, action_context: DialogueActionContext) -> None:
        action_context.player.force_walk_toward(self.x, self.y)
    def is_finished(self, action_context: DialogueActionContext) -> bool:
        return action_context.player.force_walking_toward == None

# Triggers

class DialogueTrigger:
    """Triggers an action when the rising edge of a condition is met"""
    condition: DialogueCondition
    action: DialogueAction
    rising_edge: bool = True
    has_fired: bool = False
    only_once: bool

    def __init__(self, condition: DialogueCondition, action: DialogueAction, only_once: bool = False) -> None:
        self.condition = condition
        self.action = action
        self.only_once = only_once

    def check(self, condition_state: ConditionState) -> bool:
        condition_met = self.condition.check(condition_state)
        if condition_met and self.rising_edge:
            self.rising_edge = False
            should_run = (not self.has_fired) or not self.only_once
            self.has_fired = True
            return should_run
        elif not condition_met:
            self.rising_edge = True
        return False

class DialogueManager:
    renderer: DialogueRenderer = DialogueRenderer()
    
    queue: list[list[str]] = []
    current_lines: list[str] = []
    
    condition_state: ConditionState = ConditionState()
    
    dialogue_triggers: list[DialogueTrigger] = [
        DialogueTrigger(AfterEventCondition(WorldEvent.GameStart), SequenceAction(
            SetPlayerPositionAction(MAP_WIDTH * TILE_SIZE, MAP_HEIGHT * TILE_SIZE // 2),
            ParallelAction(
                SequenceAction(
                    QueueLinesAndWaitAction("You", "I can’t wait to get out of that place…", "At last, I can relax with some simple farming!"),
                    QueueLinesAndWaitAction("You", "Oh, Doctor Whom!"),
                ),
                ForcePlayerWalkAction(MAP_WIDTH * TILE_SIZE * 0.75, MAP_HEIGHT * TILE_SIZE // 2)
            ),
            # WaitAction(0.25),
            QueueLinesAndWaitAction("Dr. Whom", "And whom might you be?", "Wait, I remember you!", "You're...     you."),
            QueueLinesAndWaitAction("Dr. Whom", "Well, anyways…", "What are you doing in these far-out lands?", "This seems uncharacteristic of you."),
            QueueLinesAndWaitAction("You", "Oh, I just wanted to relax for a bit!", "Get away from corporate life, right?", "     Haha."),
            QueueLinesAndWaitAction("Dr. Whom", "Huh. Well, I can show you the ropes around here!"),
            QueueLinesAndWaitAction("You", "I mean… I know how to walk with WASD or", "left joystick! And farming should be", "as simple as Left click or A!"),
            QueueLinesAndWaitAction("Dr. Whom", "What the #*!$?", "What are you even talking about?"),
            # WaitAction(0.25),
            QueueLinesAndWaitAction("You", "Oh… anyway.", "What else do I need to know about farming?"),
            QueueLinesAndWaitAction("Dr. Whom", "Well, not much!", "You uproot the grass to find fertile soil,", "till it, put some seeds in, and wait!"),
            QueueLinesAndWaitAction("Dr. Whom", "I’m sure Mr. Shopkeeper over here would be", "happy to show you what he has to offer!"),
            SetEventAction(WorldEvent.DrWhomShopkeeper)
        ), True),
        DialogueTrigger(AndCondition(
            AfterEventCondition(WorldEvent.DrWhomShopkeeper),
            BeforeEventCondition(WorldEvent.AfterFirstShopInteraction),
            BeforeEventCondition(WorldEvent.FirstScaryNightStart),
            
            AfterEventCondition(WorldEvent.DialogueDrWhom)
        ), SequenceAction(
            ClearEventAction(WorldEvent.DialogueDrWhom),
            QueueLinesAndWaitAction("Dr. Whom", "Go talk to the shopkeeper over there!")
        )),
        
        DialogueTrigger(AndCondition(
            AfterEventCondition(WorldEvent.DrWhomShopkeeper),
            BeforeEventCondition(WorldEvent.AfterFirstShopInteraction),
            
            AfterEventCondition(WorldEvent.DialogueMrShopkeeper)
        ), SequenceAction(
            ClearEventAction(WorldEvent.DialogueMrShopkeeper),
            QueueGameActionAction("scene:shop"),
            QueueLinesAndWaitAction("Mr. Shopkeeper", "Hey. Take a look."),
            SetEventAction(WorldEvent.AfterFirstShopInteraction)
        )),
        DialogueTrigger(AndCondition(
            AfterEventCondition(WorldEvent.AfterFirstShopInteraction),
            BeforeEventCondition(WorldEvent.SellFirstProducePrompt),
            
            AfterEventCondition(WorldEvent.DialogueMrShopkeeper)
        ), SequenceAction(
            ClearEventAction(WorldEvent.DialogueMrShopkeeper),
            QueueGameActionAction("scene:shop"),
            QueueLinesAndWaitAction("Mr. Shopkeeper", "Hey."),
        )),

        DialogueTrigger(AndCondition(
            AfterEventCondition(WorldEvent.AfterFirstShopInteraction),
            BeforeEventCondition(WorldEvent.StartFarming),
            BeforeEventCondition(WorldEvent.FirstScaryNightStart),
            
            AfterEventCondition(WorldEvent.DialogueDrWhom)
        ), SequenceAction(
            ClearEventAction(WorldEvent.DialogueDrWhom),
            QueueLinesAndWaitAction("Dr. Whom", "So...", "I see you're not doing too well financially, huh?"),
            QueueLinesAndWaitAction("You", "No, no! I'm wealthier than your wildest dreams!"),
            WaitAction(0.25),
            QueueLinesAndWaitAction("Dr. Whom", "Well, I suppose you don’t need these", "seeds and tools, then?"),
            QueueLinesAndWaitAction("You", "Well, those would be quite helpful…", "Not that I couldn’t buy them myself, of course."),
            WaitAction(0.25),
            GiveItemsAction(((Item.CARROT_SEEDS, 10), (Item.SHOVEL, 1), (Item.HOE, 1), (Item.AXE, 1), (Item.WATERING_CAN_EMPTY, 1))),
            SetEventAction(WorldEvent.StartFarming),
        ), True),
        
        DialogueTrigger(AndCondition(
            AfterEventCondition(WorldEvent.StartFarming),
            BeforeEventCondition(WorldEvent.HarvestHintDone),
            BeforeEventCondition(WorldEvent.FirstScaryNightStart),
            
            AfterEventCondition(WorldEvent.DialogueDrWhom)
        ), SequenceAction(
            ClearEventAction(WorldEvent.DialogueDrWhom),
            QueueLinesAndWaitAction("Dr. Whom", "Go out there and get farming!"),
        )),
        
        DialogueTrigger(AndCondition(
            AfterEventCondition(WorldEvent.StartFarming, 20_000),
            BeforeEventCondition(WorldEvent.ShovelHintDone)
        ), QueueLinesAndWaitAction("Dr. Whom", "What are you waiting for?", "You can use that shovel over on your new", "farm plot to the West!"), True),
        DialogueTrigger(AndCondition(
            AfterEventCondition(WorldEvent.StartFarming, 60_000),
            BeforeEventCondition(WorldEvent.ShovelHintDone)
        ), QueueLinesAndWaitAction("You", "Man, I'm such a procrastinator."), True),
        DialogueTrigger(AndCondition(
            AfterEventCondition(WorldEvent.StartFarming, 120_000),
            BeforeEventCondition(WorldEvent.ShovelHintDone)
        ), QueueLinesAndWaitAction("God", f"{get_username()}... what are you doing?"), True),
        
        DialogueTrigger(AndCondition(
            AfterEventCondition(WorldEvent.ShovelHintDone, 20_000),
            BeforeEventCondition(WorldEvent.TillHintDone)
        ), QueueLinesAndWaitAction("Dr. Whom", "You know, you can use that hoe to till the soil", "and make it ready for planting!"), True),
        DialogueTrigger(AndCondition(
            AfterEventCondition(WorldEvent.ShovelHintDone, 60_000),
            BeforeEventCondition(WorldEvent.TillHintDone)
        ), QueueLinesAndWaitAction("You", "I'm still procrastinating..."), True),
        DialogueTrigger(AndCondition(
            AfterEventCondition(WorldEvent.ShovelHintDone, 120_000),
            BeforeEventCondition(WorldEvent.TillHintDone)
        ), QueueLinesAndWaitAction("God", f"{get_username()}, this isn't funny."), True),
        
        DialogueTrigger(AndCondition(
            AfterEventCondition(WorldEvent.TillHintDone, 20_000),
            BeforeEventCondition(WorldEvent.SeedsHintDone)
        ), QueueLinesAndWaitAction("Dr. Whom", "One of the last steps is to plant those", "carrot seeds I gave you!"), True),
        DialogueTrigger(AndCondition(
            AfterEventCondition(WorldEvent.TillHintDone, 60_000),
            BeforeEventCondition(WorldEvent.SeedsHintDone)
        ), QueueLinesAndWaitAction("You", "Man, I guess I really don't want to farm today."), True),
        DialogueTrigger(AndCondition(
            AfterEventCondition(WorldEvent.TillHintDone, 120_000),
            BeforeEventCondition(WorldEvent.SeedsHintDone)
        ), QueueLinesAndWaitAction("God", f"{get_username()}... the seeds.", "The ones in your inventory."), True),
        
        DialogueTrigger(AndCondition(
            AfterEventCondition(WorldEvent.FullyGrownPlant, 20_000),
            BeforeEventCondition(WorldEvent.HarvestHintDone)
        ), QueueLinesAndWaitAction("Dr. Whom", "And now that you have some fully", "growen carrots, you can harvest them!", "Just use your hoe on them."), True),
        DialogueTrigger(AndCondition(
            AfterEventCondition(WorldEvent.FullyGrownPlant, 60_000),
            BeforeEventCondition(WorldEvent.HarvestHintDone)
        ), QueueLinesAndWaitAction("You", "Woah, those carrots are super sparkly! I should", "probably harvest them before they get too ripe."), True),
        DialogueTrigger(AndCondition(
            AfterEventCondition(WorldEvent.FullyGrownPlant, 120_000),
            BeforeEventCondition(WorldEvent.HarvestHintDone)
        ), QueueLinesAndWaitAction("God", "There are fully grown carrots on our main", f"character's farm, {get_username()}.", "You need to harvest them."), True),
        
        DialogueTrigger(AndCondition(
            AfterEventCondition(WorldEvent.HarvestHintDone),
            BeforeEventCondition(WorldEvent.SellFirstProducePrompt),
            BeforeEventCondition(WorldEvent.FirstScaryNightStart),
            
            AfterEventCondition(WorldEvent.DialogueDrWhom)
        ), SequenceAction(
            ClearEventAction(WorldEvent.DialogueDrWhom),
            SetEventAction(WorldEvent.SellFirstProducePrompt),
            QueueLinesAndWaitAction("Dr. Whom", "Hey, I see you've harvested your first crop!"),
            QueueLinesAndWaitAction("You", "Why are you still out here?"),
            QueueLinesAndWaitAction("Dr. Whom", "Whom cares? I'm just here to help you out!"),
            QueueLinesAndWaitAction("You", "Okay..."),
            QueueLinesAndWaitAction("Dr. Whom", "You should probably sell your produce to", "Mr. Shopkeeper over there!"),
            QueueGameActionAction("scary_night_occurances_start")
        ), True),
        DialogueTrigger(AndCondition(
            AfterEventCondition(WorldEvent.SellFirstProducePrompt),
            BeforeEventCondition(WorldEvent.FirstScaryNightStart),
            
            AfterEventCondition(WorldEvent.DialogueDrWhom)
        ), SequenceAction(
            ClearEventAction(WorldEvent.DialogueDrWhom),
            QueueLinesAndWaitAction("Dr. Whom", "You should probably sell your produce to", "Mr. Shopkeeper over there!"),
        )),
        DialogueTrigger(AndCondition(
            AfterEventCondition(WorldEvent.SellFirstProducePrompt),
            # BeforeEventCondition(...), todo when adding more dialogue
            
            AfterEventCondition(WorldEvent.DialogueMrShopkeeper)
        ), SequenceAction(
            ClearEventAction(WorldEvent.DialogueMrShopkeeper),
            QueueGameActionAction("scene:shop"),
            QueueLinesAndWaitAction("Mr. Shopkeeper", "I see you've got some carrots to sell!"),
            SetEventAction(WorldEvent.ScaryNightsStarted)
        )),
        
        DialogueTrigger(AfterEventCondition(WorldEvent.FirstScaryNightStart, 1_500), SequenceAction(
            QueueLinesAndWaitAction("You", "Wait, what's going on!?", "What are those... things...?"),
            QueueLinesAndWaitAction("Dr. Whom", "Oh no...", "    Oh no no no no no.", "Not tonight!"),
            QueueLinesAndWaitAction("You", "What do you mean, 'not tonight'?"),
            QueueLinesAndWaitAction("Dr. Whom", "I was worried about this...", "this is your fault, you know!"),
            QueueLinesAndWaitAction("You", "What do you mean, my fault?"),
            QueueLinesAndWaitAction("Dr. Whom", "Just worry about your crops, okay?")
        ), True),
        DialogueTrigger(AndCondition(
            AfterEventCondition(WorldEvent.FirstScaryNightStart),
            BeforeEventCondition(WorldEvent.FirstScaryNightEnd),
            
            AfterEventCondition(WorldEvent.DialogueDrWhom)
        ), SequenceAction(
            ClearEventAction(WorldEvent.DialogueDrWhom),
            QueueLinesAndWaitAction("Dr. Whom", "Worry about your crops!!"),
        )),
        DialogueTrigger(AfterEventCondition(WorldEvent.FirstScaryNightEnd, 1_500), SequenceAction(
            RaceAction(
                # Make player walk to the front of the house but teleport if they take too long
                ForcePlayerWalkAction(MAP_WIDTH * TILE_SIZE * 0.75, MAP_HEIGHT * TILE_SIZE // 2),
                SequenceAction(WaitAction(15), SetPlayerPositionAction(MAP_WIDTH * TILE_SIZE * 0.75, MAP_HEIGHT * TILE_SIZE // 2))
            ),
            QueueLinesAndWaitAction("You", "What were those... shadow figures?!"),
            QueueLinesAndWaitAction("Dr. Whom", "Look, I don't have time to explain right now.", "Just... keep farming, okay?"),
            # TODO: Dr. Whom walks off screen
            WaitAction(1),
            QueueLinesAndWaitAction("You", "I guess it's just me and my crops now...", "And Mr. Shopkeeper, I guess."),
        ), True),
    ]
    running_actions: list[DialogueAction] = []

    def queue_dialogue(self, lines: list[str]):
        self.queue.append(list(lines)) # Copy the list to prevent modification of the original
        if not self.is_shown():
            self.renderer.reset()
            self.current_lines = self.queue.pop(0)
    
    def on_confirm(self):
        if self.is_active():
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
    
    def update(self, delta: float, audio_manager: AudioManager, player: "Player") -> list[str]:
        """
        Returns a list of queued game actions. These are currently just scene names to switch to.
        This could be an enum... or we could restructure this to not need it at all... but I'm
        lazy and don't have enough time to mess with refactors.
        """
        action_context = DialogueActionContext(self, audio_manager, player)
        for trigger in self.dialogue_triggers:
            if trigger.check(self.condition_state):
                trigger.action.start(action_context)
                self.running_actions.append(trigger.action)
        for action in self.running_actions:
            action.update(action_context, delta)
            if action.is_finished(action_context):
                action.end(action_context)
                self.running_actions.remove(action)
        
        if self.is_active():
            self.renderer.update(self.current_lines, delta, audio_manager)
        
        return action_context.queued_game_actions

    def add_game_message(self, message: str):
        """
        Adds a message to the list of events that the game sends to the dialogue system. These are currently just strings.
        This could be an enum... or we could restructure this to not need it at all... but I'm lazy and don't have enough
        time to mess with refactors.
        """
        self.condition_state.game_messages.add(message)
    
    def draw(self, win: pygame.Surface):
        if len(self.current_lines):
            self.renderer.draw(win, self.current_lines)