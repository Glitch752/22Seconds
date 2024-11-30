
import math
import random
from typing import Self
import pygame

from constants import CROSSHAIR_COLOR, CROSSHAIR_ONLY_WITH_JOYSTICK, CROSSHAIR_SIZE, CROSSHAIR_THICKNESS, DAY_LENGTH, DUSK_DAWN_LENGTH, HEIGHT, MAP_HEIGHT, MAP_WIDTH, NIGHT_LENGTH, NIGHT_OPACITY, TILE_SIZE, WIDTH
from dialogue import WorldEvent
from game import Game
from game_scene import GameScene
from graphics import WHITE_IMAGE, big_font_render, giant_font_render
from graphics.floating_hint_text import draw_floating_hint_texts
from graphics.particles import draw_particles, update_particles
from inputs import InputType, Inputs
from map import Map
from player import Player
from utils import clamp, ease

NON_INTERACTABLE_SELECTION_COLOR = 'yellow'
INTERACTABLE_SELECTION_COLOR = 'green'
NOTHING_SELECTION_COLOR = 'gray'

def draw_currency(win: pygame.Surface, player: Player):
    win.blit(big_font_render(f"Currency: {player.currency}c", 'black'), (17, 17))
    win.blit(big_font_render(f"Currency: {player.currency}c", 'yellow'), (15, 15))
def draw_time(win: pygame.Surface, day_cycle_time: float):
    t = day_cycle_time / (DAY_LENGTH + NIGHT_LENGTH) * 24
    time = f"{str(int(t)).rjust(2, '0')}:{str(int((t % 1) * 60)).rjust(2, '0')}"
    
    win.blit(surface := big_font_render(time, 'black'), (17, HEIGHT - 15 - surface.get_height()))
    win.blit(surface := big_font_render(time, 'green'), (15, HEIGHT - 17 - surface.get_height()))

# TODO: Only instantiate once and convert day cycle to a class stored here
class PlayingGameScene(GameScene):
    selected_cell_x: int = 0
    selected_cell_y: int = 0
    target_x: float = 0
    target_y: float = 0
    farm: Map = Map()
    
    selection_color: str = NOTHING_SELECTION_COLOR
    camera_position: pygame.Vector2
    
    day_cycle_time: float = 0
    was_day: bool = True
    day_fade_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    
    def __init__(self: Self, game: Game):
        super().__init__(game)
        self.camera_position = game.player.pos.copy()
        
        self.day_fade_surface.fill((0, 0, 15))
    
    def enter(self: Self):
        self.game.audio_manager.play_day_track()
        self.game.dialogue_manager.condition_state.add_event(WorldEvent.GameStart)
    
    def get_target_reference(self: Self):
        return self.game.player.pos - self.camera_position + pygame.Vector2(WIDTH // 2, HEIGHT // 2)
    
    def update(self: Self, inputs: Inputs, dt: float):
        player = self.game.player
        player.update(inputs.movement_x, inputs.movement_y, self.farm, dt)
        
        # Interaction
        mx, my = pygame.mouse.get_pos()
        if player.over_ui(mx, my):
            self.selection_color = NOTHING_SELECTION_COLOR
        else:
            selected_item = player.get_selected_item()
            
            self.selected_cell_x = math.floor((inputs.target_x + player.pos.x) // TILE_SIZE)
            self.selected_cell_y = math.floor((inputs.target_y + player.pos.y) // TILE_SIZE)
            self.target_x = inputs.target_x
            self.target_y = inputs.target_y
            if selected_item == None:
                interaction = None
            else:
                interaction = self.farm.get_interaction(self.selected_cell_x, self.selected_cell_y, selected_item, player, self.game.audio_manager)
            self.selection_color = INTERACTABLE_SELECTION_COLOR if interaction else NON_INTERACTABLE_SELECTION_COLOR

            if interaction != None:
                if inputs.interaction:
                    if not player.wait_for_mouseup:
                        result = interaction()
                        if result == -1:
                            player.decrement_selected_item_quantity()
                else:
                    player.wait_for_mouseup = False
        
        # General updates
        update_particles(dt)
        self.farm.update(self.game.audio_manager)
        
        camera_target = player.pos.copy()
        camera_target.x = clamp(camera_target.x, WIDTH // 2, TILE_SIZE * MAP_WIDTH - WIDTH // 2)
        camera_target.y = clamp(camera_target.y, HEIGHT // 2, TILE_SIZE * MAP_HEIGHT - HEIGHT // 2)
        
        self.camera_position = self.camera_position.lerp(camera_target, 0.05)

        # Update day cycle
        cycle_length = DAY_LENGTH + NIGHT_LENGTH
        self.day_cycle_time += dt
        self.day_cycle_time %= cycle_length
        
        is_day = self.day_cycle_time < DAY_LENGTH
        if is_day != self.was_day:
            self.was_day = is_day
            if is_day:
                self.day_transition()
            else:
                self.night_transition()

    def day_transition(self: Self):
        """Called when the day starts"""
        import game_scene.in_shop
        self.game.update_scene(game_scene.in_shop.InShopScene(self.game))
        self.game.audio_manager.play_day_track()

    def night_transition(self: Self):
        """Called when the night starts"""
        # TODO: Sound effects
        self.game.audio_manager.play_night_track()

    def get_daylight(self: Self):
        """Returns a value from 0 to 1 representing the current daylight. Throughout the entire night, this value is 0."""
        if self.day_cycle_time < DUSK_DAWN_LENGTH:
            return ease(self.day_cycle_time / DUSK_DAWN_LENGTH)
        elif self.day_cycle_time < DAY_LENGTH - DUSK_DAWN_LENGTH:
            return 1
        elif self.day_cycle_time < DAY_LENGTH:
            return ease(1 - (self.day_cycle_time - (DAY_LENGTH - DUSK_DAWN_LENGTH)) / DUSK_DAWN_LENGTH)
        else:
            return 0
    
    def draw(self: Self, win: pygame.Surface):
        win.fill("#000000")
        
        self.farm.draw(win, self.camera_position)
        
        # Draw outline
        x = self.selected_cell_x * TILE_SIZE - self.camera_position.x + WIDTH // 2
        y = self.selected_cell_y * TILE_SIZE - self.camera_position.y + HEIGHT // 2
        win.blit(WHITE_IMAGE, (x, y))
        pygame.draw.rect(win, self.selection_color, (x, y, TILE_SIZE, TILE_SIZE), 1)
        
        # Draw target crosshair
        if not CROSSHAIR_ONLY_WITH_JOYSTICK or not self.game.inputs.using_keyboard_input:
            target_reference = self.get_target_reference()
            pygame.draw.line(
                win, CROSSHAIR_COLOR,
                (target_reference.x + self.target_x - CROSSHAIR_SIZE, target_reference.y + self.target_y),
                (target_reference.x + self.target_x + CROSSHAIR_SIZE, target_reference.y + self.target_y),
                width=CROSSHAIR_THICKNESS
            )
            pygame.draw.line(
                win, CROSSHAIR_COLOR,
                (target_reference.x + self.target_x, target_reference.y + self.target_y - CROSSHAIR_SIZE),
                (target_reference.x + self.target_x, target_reference.y + self.target_y + CROSSHAIR_SIZE),
                width=CROSSHAIR_THICKNESS
            )
        
        draw_particles(win, self.camera_position)
        self.game.player.draw_player(win, self.camera_position)
        
        # Draw day fading
        brightness = self.get_daylight()
        self.day_fade_surface.set_alpha(int((1 - brightness) * NIGHT_OPACITY))
        win.blit(self.day_fade_surface, (0, 0))
        
        draw_floating_hint_texts(win, self.camera_position)
        
        self.game.player.draw_ui(win)
        
        if self.get_daylight() == 0:
            # It's night... spooky
            time_remaining = NIGHT_LENGTH - (self.day_cycle_time - DAY_LENGTH)
            shake_amount = int(2 / max(0.5, time_remaining / NIGHT_LENGTH) + 0.5)
            # Only works for <60 second nights, whatever for now
            win.blit(
                font := giant_font_render(f"00:{str(int(time_remaining)).rjust(2, '0')}", "red"),
                (WIDTH // 2 - font.get_width() // 2 + random.randint(-shake_amount, shake_amount), 15 + random.randint(-shake_amount,shake_amount))
            )
        
        draw_currency(win, self.game.player)
        draw_time(win, self.day_cycle_time)
    
    def event_input(self: Self, type: InputType):
        if type.is_slot_select():
            player = self.game.player
            player_slots = len(player.get_interactable_items())
            slot = type.get_slot_index(player_slots - player.selected_slot, player_slots)
            player.select_slot(player_slots - slot)
            return

        if type == InputType.CLICK_DOWN or pygame.mouse.get_pressed(3)[0]:
            self.game.player.mouse_down()
            self.game.inputs.interaction = True
            return

        if type == InputType.CLICK_UP or not pygame.mouse.get_pressed(3)[0]:
            self.game.inputs.interaction = False
            return