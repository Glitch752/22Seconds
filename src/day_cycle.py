import pygame
from constants import DAY_LENGTH, NIGHT_LENGTH
import os

day_song = pygame.mixer.Sound(os.path.join("assets", "audio", "track2.wav"))
night_song = pygame.mixer.Sound(os.path.join("assets", "audio", "track2.wav"))

day_cycle_time = 0

def update_day_cycle(delta):
    global day_cycle_time
    day_cycle_time += delta

def get_brightness():
    global day_cycle_time
    
    t = abs(day_cycle_time % 2 - 1)
    return 0 if t == 0 else (1 if t == 1 else (pow(2, 20 * t - 10) / 2 if t < 0.5 else 2 - pow(2, -20 * t + 10) / 2))