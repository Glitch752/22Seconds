from typing import Self
from enum import Enum, auto
import pygame
import math

from constants import TARGET_RADIUS
from graphics import get_height, get_width

def deadzone(x, z=0.1):
    if abs(x) >= z:
        return (x - z) / (1 - z)
    return 0

class InputType(Enum):
    SELECT_SLOT_1 = auto() # 1 for keyboard
    SELECT_SLOT_2 = auto() # 2 for keyboard
    SELECT_SLOT_3 = auto() # 3 for keyboard
    SELECT_SLOT_4 = auto() # 4 for keyboard
    SELECT_SLOT_5 = auto() # 5 for keyboard
    SELECT_SLOT_6 = auto() # 6 for keyboard
    SELECT_SLOT_7 = auto() # 7 for keyboard
    SELECT_SLOT_8 = auto() # 8 for keyboard
    SELECT_SLOT_9 = auto() # 9 for keyboard
    SELECT_SLOT_10 = auto() # 0 for keyboard
    
    CLICK_DOWN = auto() # LMB for mouse, A for controller
    CLICK_UP = auto() # LMB for mouse, A for controller
    ALTERNATE_CLICK_DOWN = auto() # RMB for mouse, X for controller
    ALTERNATE_CLICK_UP = auto() # RMB for mouse, X for controller
    
    INVENTORY_SCROLL_UP = auto() # Scroll up for mouse (fired once per scroll tick), left bumper for controller
    INVENTORY_SCROLL_DOWN = auto() # Scroll down for mouse (fired once per scroll tick), right bumper for controller
    
    INTERACT_DOWN = auto() # E/Z/space for keyboard, A for controller
    INTERACT_UP = auto() # E/Z/space for keyboard, A for controller
    
    CANCEL = auto() # ESC for keyboard, B for controller
    
    def get_slot_index(self, current_slot: int, slot_count: int) -> int:
        if self == InputType.INVENTORY_SCROLL_UP:
            return max(1, min(slot_count, current_slot - 1))
        if self == InputType.INVENTORY_SCROLL_DOWN:
            return max(1, min(slot_count, current_slot + 1))
        
        # This depends on the select slot input type being in order,
        # which is a bit of a hack but it's fine for now
        return max(1, min(slot_count, self.value - InputType.SELECT_SLOT_1.value + 1))
    
    def is_slot_select(self) -> bool:
        return self in {
            InputType.SELECT_SLOT_1, InputType.SELECT_SLOT_2, InputType.SELECT_SLOT_3, InputType.SELECT_SLOT_4, InputType.SELECT_SLOT_5,
            InputType.SELECT_SLOT_6, InputType.SELECT_SLOT_7, InputType.SELECT_SLOT_8, InputType.SELECT_SLOT_9, InputType.SELECT_SLOT_10,
            InputType.INVENTORY_SCROLL_UP, InputType.INVENTORY_SCROLL_DOWN
        }
    
    @staticmethod
    def from_keyboard_input(key: int, down: bool) -> Self:
        match key:
            case pygame.K_1:
                return InputType.SELECT_SLOT_1 if down else None
            case pygame.K_2:
                return InputType.SELECT_SLOT_2 if down else None
            case pygame.K_3:
                return InputType.SELECT_SLOT_3 if down else None
            case pygame.K_4:
                return InputType.SELECT_SLOT_4 if down else None
            case pygame.K_5:
                return InputType.SELECT_SLOT_5 if down else None
            case pygame.K_6:
                return InputType.SELECT_SLOT_6 if down else None
            case pygame.K_7:
                return InputType.SELECT_SLOT_7 if down else None
            case pygame.K_8:
                return InputType.SELECT_SLOT_8 if down else None
            case pygame.K_9:
                return InputType.SELECT_SLOT_9 if down else None
            case pygame.K_0:
                return InputType.SELECT_SLOT_10 if down else None
            case pygame.K_z:
                return InputType.CLICK_DOWN if down else InputType.CLICK_UP
            case pygame.K_x:
                return InputType.ALTERNATE_CLICK_DOWN if down else InputType.ALTERNATE_CLICK_UP
            case pygame.K_ESCAPE:
                return InputType.CANCEL
            case pygame.K_e | pygame.K_z | pygame.K_SPACE:
                return InputType.INTERACT_DOWN if down else InputType.INTERACT_UP
            case _:
                return None
    
    @staticmethod
    def from_mouse_input(button: int, down: bool) -> Self:
        match button:
            case pygame.BUTTON_LEFT:
                return InputType.CLICK_DOWN if down else InputType.CLICK_UP
            case pygame.BUTTON_RIGHT:
                return InputType.ALTERNATE_CLICK_DOWN if down else InputType.ALTERNATE_CLICK_UP
            case _:
                return None
    
    @staticmethod
    def from_controller_input(button: int, down: bool) -> Self:
        match button:
            case pygame.CONTROLLER_BUTTON_RIGHTSTICK:
                return InputType.CLICK_DOWN if down else InputType.CLICK_UP
            case pygame.CONTROLLER_BUTTON_X:
                return InputType.ALTERNATE_CLICK_DOWN if down else InputType.ALTERNATE_CLICK_UP
            case pygame.CONTROLLER_BUTTON_LEFTSHOULDER:
                return InputType.INVENTORY_SCROLL_UP if down else None
            case pygame.CONTROLLER_BUTTON_RIGHTSHOULDER:
                return InputType.INVENTORY_SCROLL_DOWN if down else None
            case pygame.CONTROLLER_BUTTON_B:
                return InputType.CANCEL if down else None
            case pygame.CONTROLLER_BUTTON_A:
                return InputType.INTERACT_DOWN if down else InputType.INTERACT_UP
            case _:
                return None
            

class Inputs:
    movement_x: float
    movement_y: float
    
    # For selecting tiles with joysticks
    joysticks: list[pygame.joystick.Joystick]
    using_keyboard_input: bool
    
    # Determined by the right joystick when using a controller,
    # and the mouse when using keyboard input
    target_x: float
    target_y: float

    clicking: bool = False
    interacting: bool = False
    click_rising_edge: bool = False
    
    def __init__(self):
        self.joystick_update()
    
    def input_event(self, input_type: InputType):
        if input_type == InputType.CLICK_DOWN:
            self.clicking = True
        elif input_type == InputType.CLICK_UP:
            self.clicking = False
            self.click_rising_edge = True
        elif input_type == InputType.INTERACT_DOWN:
            self.interacting = True
        elif input_type == InputType.INTERACT_UP:
            self.interacting = False
    
    def joystick_update(self):
        self.joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
        self.using_keyboard_input = len(self.joysticks) == 0
    
    def update(self: Self, target_reference: pygame.Vector2 = pygame.Vector2(get_width() // 2, get_height() // 2)):
        if self.using_keyboard_input:
            self.movement_x = 0
            self.movement_y = 0
            keys = pygame.key.get_pressed()
            if keys[pygame.K_w] or keys[pygame.K_UP]:
                self.movement_y -= 1
            if keys[pygame.K_s] or keys[pygame.K_DOWN]:
                self.movement_y += 1
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                self.movement_x -= 1
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                self.movement_x += 1
            
            mouse_x, mouse_y = pygame.mouse.get_pos()
            self.target_x = mouse_x - target_reference.x
            self.target_y = mouse_y - target_reference.y
        else:
            joystick = self.joysticks[0]
            self.movement_x = deadzone(joystick.get_axis(pygame.CONTROLLER_AXIS_LEFTX))
            self.movement_y = deadzone(joystick.get_axis(pygame.CONTROLLER_AXIS_LEFTY))
            
            self.target_x = deadzone(joystick.get_axis(pygame.CONTROLLER_AXIS_RIGHTX)) * TARGET_RADIUS
            self.target_y = deadzone(joystick.get_axis(pygame.CONTROLLER_AXIS_RIGHTY)) * TARGET_RADIUS
        
        target_mag = math.sqrt(self.target_x ** 2 + self.target_y ** 2)
        self.target_x = self.target_x / target_mag * TARGET_RADIUS if target_mag > TARGET_RADIUS else self.target_x
        self.target_y = self.target_y / target_mag * TARGET_RADIUS if target_mag > TARGET_RADIUS else self.target_y
        
        movement_mag = math.sqrt(self.movement_x ** 2 + self.movement_y ** 2)
        self.movement_x = self.movement_x / movement_mag if movement_mag > 1 else self.movement_x
        self.movement_y = self.movement_y / movement_mag if movement_mag > 1 else self.movement_y
        
        if self.click_rising_edge and self.clicking:
            self.click_rising_edge = False