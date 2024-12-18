import pygame
from audio import AudioManager, SoundType
from constants import SLOT_BACKGROUND
from graphics import get_width, normal_font_render, small_font_render
from items import ITEM_SLOT_BORDER_RADIUS

class DialogueRenderer:
    current_char: int = 0
    current_line: int = 0
    timer: float = 0
    done: bool = False
    time_per_letter: float = 1 / 60
    talking_sound_counter: int = 0
    letters_per_talking_sound: int = 3
    
    def reset(self):
        self.done = False
        self.current_char = 0
        self.current_line = 0
    
    def skip_to_end(self, lines: list[str]):
        self.done = True
        self.current_line = len(lines) - 1
        self.current_char = len(lines[self.current_line])
    
    def draw(self, win: pygame.Surface, lines: list[str]):
        pygame.draw.rect(
            win,
            SLOT_BACKGROUND,
            pygame.Rect(get_width() // 2 - 300, 20, 600, len(lines) * 30 + 30),
            border_radius=ITEM_SLOT_BORDER_RADIUS
        )

        y = 25

        for i, line in enumerate(lines):
            if i <= self.current_line:
                if i == 0:
                    t = normal_font_render(line if i != self.current_line else line[:self.current_char], 'white')
                else:
                    t = small_font_render(line if i != self.current_line else line[:self.current_char], 'white')

                win.blit(t, (16 + get_width() // 2 - 295, 16 + y))
                
                y += t.get_height() + 5
    
    def update(self, lines: list[str], delta: float, audio_manager: AudioManager):
        self.timer += delta

        if self.timer > self.time_per_letter:
            self.timer -= self.time_per_letter

            self.current_char += 1
            
            if self.current_char == len(lines[self.current_line]):
                self.current_line += 1

                if self.current_line > len(lines) - 1:
                    self.current_line = len(lines) - 1
                    self.done = True
                    return
                
                self.current_char = 0
            elif lines[self.current_line][self.current_char] != " ":
                if self.talking_sound_counter >= self.letters_per_talking_sound:
                    audio_manager.play_sound(SoundType.SPEAKING_SOUND)
                    self.talking_sound_counter = 0
                self.talking_sound_counter += 1