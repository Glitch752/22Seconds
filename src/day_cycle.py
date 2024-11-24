import pygame
from constants import DAY_LENGTH, NIGHT_LENGTH, DUSK_DAWN_LENGTH, WIDTH, HEIGHT
from graphics import giant_font_render
import os
import random

day_song = pygame.mixer.Sound(os.path.join("assets", "audio", "main_track.wav"))
night_song = pygame.mixer.Sound(os.path.join("assets", "audio", "track2.wav"))

day_cycle_time = 0
was_day = True

day_face_surface = pygame.Surface((WIDTH, HEIGHT))
day_face_surface.fill((0, 0, 15))
NIGHT_OPACITY = 150

cha_ching_sound = pygame.mixer.Sound(os.path.join("assets", "audio", "chaChing.wav"))
transformation_sound_effect = pygame.mixer.Sound(os.path.join("assets", "audio", "transformation.wav"))
transformation_sound_effect.set_volume(2.0)

queued_sounds = []

def update_day_cycle(delta, player):
    global day_cycle_time, was_day
    
    cycle_length = DAY_LENGTH + NIGHT_LENGTH
    day_cycle_time += delta
    day_cycle_time %= cycle_length
    
    is_day = day_cycle_time < DAY_LENGTH
    if is_day != was_day:
        was_day = is_day
        if is_day:
            day_transition(player)
        else:
            night_transition(player)

def day_transition(player):
    from main import set_game_state, GameState, player
    print("DAYSLIFU")
    set_game_state(GameState.InShop)
    player.sell_items()
    sounds = player.profit // 10 + 1
    for i in range(sounds):
        queued_sounds.append((pygame.time.get_ticks() + i * 100, cha_ching_sound))
    pygame.mixer.music.stop()
    pygame.mixer.music.load(os.path.join("assets", "audio", "shop_track.wav"))
    pygame.mixer.music.play()
    player.crazed = False

def night_transition(player):
    print("NIGHTSLIFU")
    pygame.mixer.music.stop()
    pygame.mixer.music.load(os.path.join("assets", "audio", "track2.wav"))
    pygame.mixer.music.play()
    player.crazed = True
    transformation_sound_effect.play()

# TODO: wtf refactor this out of day_cycle lol
def play_sounds():
    i = 0
    while i < len(queued_sounds):
        sound = queued_sounds[i]
        if sound[0] <= pygame.time.get_ticks():
            sound[1].play()
            queued_sounds.pop(i)
            i -= 1
        i += 1
    

def draw_day_fading(win: pygame.Surface):
    global day_cycle_time
    
    brightness = get_brightness()
    day_face_surface.set_alpha(int((1 - brightness) * NIGHT_OPACITY))
    win.blit(day_face_surface, (0, 0))

    if brightness == 0:
        # It's night... spooky
        time_remaining = NIGHT_LENGTH - (day_cycle_time - DAY_LENGTH)
        shake_amount = int(3 / max(0.5, time_remaining / NIGHT_LENGTH)) + 1
        # Only works for <60 second nights, whatever for now
        win.blit(
            font := giant_font_render(f"00:{str(int(time_remaining)).rjust(2, '0')}", "red"),
            (WIDTH // 2 - font.get_width() // 2 + random.randint(-shake_amount,shake_amount), 15 + random.randint(-shake_amount,shake_amount))
        )
        pass

def ease(t):
    return t * t * (3 - 2 * t)

def get_brightness():
    global day_cycle_time
    if day_cycle_time < DUSK_DAWN_LENGTH:
        return ease(day_cycle_time / DUSK_DAWN_LENGTH)
    elif day_cycle_time < DAY_LENGTH - DUSK_DAWN_LENGTH:
        return 1
    elif day_cycle_time < DAY_LENGTH:
        return ease(1 - (day_cycle_time - (DAY_LENGTH - DUSK_DAWN_LENGTH)) / DUSK_DAWN_LENGTH)
    else:
        return 0

def get_formatted_time():
    global day_cycle_time
    
    t = day_cycle_time / (DAY_LENGTH + NIGHT_LENGTH) * 24
    return f"{str(int(t)).rjust(2, '0')}:{str(int((t % 1) * 60)).rjust(2, '0')}"