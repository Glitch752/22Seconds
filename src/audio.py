import os
from typing import Self

import pygame

class SoundType:
    BUY_ITEM = "chaChing.wav"
    NO_MONEY = "Aeeaahghgh.wav"
    TILL_SOIL = "till.wav"
    HARVEST_PLANT = "pickUp.wav"
    PLANT = "plant.wav"

class AudioManager:
    day_track: str = os.path.join("assets", "audio", "main_track.wav")
    night_track: str = os.path.join("assets", "audio", "track2.wav")
    shop_track: str = os.path.join("assets", "audio", "shop_track.wav")
    current_track: str = ""
    
    queued_sounds: list[tuple[int, pygame.mixer.Sound]] = []
    
    sounds = {}
    
    def __init__(self: Self):
        for sound in dir(SoundType):
            if sound.startswith("__"):
                continue
            sound_path = getattr(SoundType, sound)
            sound_value = pygame.mixer.Sound(os.path.join("assets", "audio", sound_path))
            self.sounds[sound] = self.sounds[sound_path] = sound_value
    
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
    
    def play_sound(self: Self, sound: str, delay: int = 0):
        self.queued_sounds.append((pygame.time.get_ticks() + delay, self.sounds[sound]))