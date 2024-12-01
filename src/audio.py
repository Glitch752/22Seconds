from enum import Enum
import random
from typing import Self

import pygame

from utils import get_asset

class SoundType(Enum):
    """Enum for all the sound types in the game. If a sound's value is a list of strings, the sound will randomly play one of the sounds in the list."""
    BUY_ITEM = "chaChing.wav"
    NO_MONEY = "Aeeaahghgh.wav"
    TILL_SOIL = "till.wav"
    HARVEST_PLANT = "pickUp.wav"
    PLANT = "plant.wav"
    WATER = "water.wav"
    SPEAKING_SOUND = [f"speak_{str(idx).rjust(2, '0')}.wav" for idx in range(1, 15)]
    CRUNCH = "crunch.wav"
    
    def __init__(self, paths: str | list[str]):
        if isinstance(paths, str):
            paths = [paths]
        
        self.paths = paths
        self.sounds = [pygame.mixer.Sound(get_asset("audio", path)) for path in paths]
    
    def get_sound(self: Self):
        return self.sounds[random.randint(0, len(self.sounds) - 1)]

class AudioManager:
    day_track: str = get_asset("audio", "main_track.wav")
    night_track: str = get_asset("audio", "track2.wav")
    shop_track: str = get_asset("audio", "shop_track.wav")
    current_track: str = ""
    
    queued_sounds: list[tuple[int, pygame.mixer.Sound]] = []
    
    def play_day_track(self: Self):
        if self.current_track == self.day_track:
            return
        self.current_track = self.day_track
        pygame.mixer.music.load(self.day_track)
        pygame.mixer.music.play(-1)
    
    def play_night_track(self: Self):
        if self.current_track == self.night_track:
            return
        self.current_track = self.night_track
        pygame.mixer.music.load(self.night_track)
        pygame.mixer.music.play(-1)
    
    def play_shop_track(self: Self):
        if self.current_track == self.shop_track:
            return
        self.current_track = self.shop_track
        pygame.mixer.music.load(self.shop_track)
        pygame.mixer.music.play(-1)
    
    def update(self: Self):
        self.play_sounds()
    
    def play_sounds(self: Self):
        i = 0
        while i < len(self.queued_sounds):
            sound = self.queued_sounds[i]
            if sound[0] <= pygame.time.get_ticks():
                sound[1].play()
                self.queued_sounds.pop(i)
                i -= 1
            i += 1
    
    def play_sound(self: Self, sound: SoundType, delay_ms: int = 0):
        self.queued_sounds.append((pygame.time.get_ticks() + delay_ms, sound.get_sound()))