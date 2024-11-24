import pygame
from constants import DAY_LENGTH, NIGHT_LENGTH, DUSK_DAWN_LENGTH, WIDTH, HEIGHT
import os

day_song = pygame.mixer.Sound(os.path.join("assets", "audio", "track2.wav"))
night_song = pygame.mixer.Sound(os.path.join("assets", "audio", "track2.wav"))

day_cycle_time = 0

day_face_surface = pygame.Surface((WIDTH, HEIGHT))
day_face_surface.fill((0, 0, 15))
NIGHT_OPACITY = 150

def update_day_cycle(delta):
    global day_cycle_time
    day_cycle_time += delta

def draw_day_fading(win: pygame.Surface):
    day_face_surface.set_alpha(int((1 - get_brightness()) * NIGHT_OPACITY))
    win.blit(day_face_surface, (0, 0))

def ease(t):
    return t * t * (3 - 2 * t)

def get_brightness():
    global day_cycle_time
    
    cycle_length = DAY_LENGTH + NIGHT_LENGTH
    cycle_time = day_cycle_time % cycle_length
    
    if cycle_time < DUSK_DAWN_LENGTH:
        return ease(cycle_time / DUSK_DAWN_LENGTH)
    elif cycle_time < DAY_LENGTH - DUSK_DAWN_LENGTH:
        return 1
    elif cycle_time < DAY_LENGTH:
        return ease(1 - (cycle_time - (DAY_LENGTH - DUSK_DAWN_LENGTH)) / DUSK_DAWN_LENGTH)
    else:
        return 0