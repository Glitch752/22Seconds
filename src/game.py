from dialogue import DialogueManager
import game_scene
from graphics import WIN, draw_all_deferred
from inputs import InputType, Inputs
from audio import AudioManager
from player import Player
import constants
import pygame

# Stores global state required throughout the game
class Game:
    player: Player
    dialogue_manager: DialogueManager = DialogueManager()
    
    current_scene: game_scene.GameScene
    
    audio_manager: AudioManager = AudioManager()
    
    should_quit_game: bool = False
    inputs: Inputs = Inputs()
    
    # This is kind of a hacky way to structure this, but it works...
    playing_game_scene: game_scene.GameScene
    
    def __init__(self):
        import game_scene.playing
        
        self.player = Player(
            constants.MAP_WIDTH * constants.TILE_SIZE // 2,
            constants.MAP_HEIGHT * constants.TILE_SIZE // 2,
            constants.TILE_SIZE // 2 - 10
        )
        self.playing_game_scene = game_scene.playing.PlayingGameScene(self)
    
    def check_keyboard_input(self):
        return len(self.joysticks) == 0
    
    def update_scene(self, new_scene: game_scene.GameScene):
        self.current_scene.exit()
        self.current_scene = new_scene
        self.current_scene.enter()
        
        self.dialogue_manager.add_game_message("exit:" + self.current_scene.name)
        self.dialogue_manager.add_game_message("enter:" + new_scene.name)

    def enter_playing_scene(self):
        self.update_scene(self.playing_game_scene)
    
    def start(self, initial_scene: game_scene.GameScene):
        self.current_scene = initial_scene
        self.current_scene.enter()
    
    def run(self, delta: float):
        self.inputs.update(self.current_scene.get_target_reference())
        
        for event in pygame.event.get():
            self.handle_event(event)
        
        queued_game_actions = self.dialogue_manager.update(delta, self.audio_manager, self.player)
        for action in queued_game_actions:
            match action:
                case "scene:shop":
                    from game_scene.in_shop import InShopScene
                    self.update_scene(InShopScene(self))
                case "scary_night_occurances_start":
                    # Wow this is so hacky but I have 15 minutes before submission
                    from game_scene.playing import PlayingGameScene
                    if isinstance(self.current_scene, PlayingGameScene):
                        self.current_scene.scary_night_occurances_started = True
                case _:
                    print(f"Unknown queued game action: {action}")
        
        self.current_scene.update(self.inputs, delta)
        self.audio_manager.update()
        
        self.current_scene.draw(WIN, self.inputs)
        self.dialogue_manager.draw(WIN)
        
        draw_all_deferred()
        
        pygame.display.flip()
    
    def handle_event(self, event: pygame.Event):
        if event.type == pygame.QUIT:
            self.should_quit_game = True
            return
        
        if event.type == pygame.JOYDEVICEADDED or event.type == pygame.JOYDEVICEREMOVED:
            self.inputs.joystick_update()
            return
        
        if self.dialogue_manager.is_shown() and event.type in [pygame.KEYDOWN, pygame.JOYBUTTONDOWN, pygame.MOUSEBUTTONDOWN]:
            self.dialogue_manager.on_confirm()
            return
        
        if event.type == pygame.KEYDOWN:
            input_type = InputType.from_keyboard_input(event.key, True)
            if input_type is not None:
                self.current_scene.event_input(input_type)
                self.inputs.input_event(input_type)
            return
        if event.type == pygame.KEYUP:
            input_type = InputType.from_keyboard_input(event.key, False)
            if input_type is not None:
                self.current_scene.event_input(input_type)
                self.inputs.input_event(input_type)
            return
        
        if event.type == pygame.JOYBUTTONDOWN:
            input_type = InputType.from_controller_input(event.button, True)
            if input_type is not None:
                self.current_scene.event_input(input_type)
                self.inputs.input_event(input_type)
            return
        if event.type == pygame.JOYBUTTONUP:
            input_type = InputType.from_controller_input(event.button, False)
            if input_type is not None:
                self.current_scene.event_input(input_type)
                self.inputs.input_event(input_type)
            return
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            input_type = InputType.from_mouse_input(event.button, True)
            if input_type is not None:
                self.current_scene.event_input(input_type)
                self.inputs.input_event(input_type)
            return
        if event.type == pygame.MOUSEBUTTONUP:
            input_type = InputType.from_mouse_input(event.button, False)
            if input_type is not None:
                self.current_scene.event_input(input_type)
                self.inputs.input_event(input_type)
            return
        if event.type == pygame.MOUSEWHEEL:
            if event.y > 0:
                for _ in range(event.y):
                    self.current_scene.event_input(InputType.INVENTORY_SCROLL_UP)
            else:
                for _ in range(-event.y):
                    self.current_scene.event_input(InputType.INVENTORY_SCROLL_DOWN)
            return
        
        #     elif event.type == pygame.MOUSEBUTTONDOWN:
        #         if event.button == 1:
        #             if game_state == GameState.Playing: # LMB
        #                 player.mouse_down(mx, my)
        #             elif game_state == GameState.InShop:
        #                 shop_click(mx, my)