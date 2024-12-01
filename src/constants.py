# Positive x is right, positive y is down
# Tile grid is based on top left of tiles

from utils import is_web


GAME_NAME = "22 Seconds"

if is_web():
    from platform import window
    DEFAULT_WIDTH, DEFAULT_HEIGHT = window.innerWidth, window.innerHeight
    # TODO: Resize when the window resizes
else:
    DEFAULT_WIDTH, DEFAULT_HEIGHT = 1280, 720

TILE_SIZE = 80

# DAY_LENGTH = 120 # Seconds
# DUSK_DAWN_LENGTH = 10 # Seconds
DAY_LENGTH = 5 # Seconds
DUSK_DAWN_LENGTH = 2 # Seconds
NIGHT_LENGTH = 22 # Seconds

TARGET_RADIUS = TILE_SIZE * 2 # Pixels

# Map stuff
MAP_WIDTH = 60
MAP_HEIGHT = 35
FARMABLE_MAP_START = (1, 1)
FARMABLE_MAP_END = (34, 34)

MAP_UPDATE_RATE = 750
PARTICLES_PER_TILE_SECOND = 5
RANDOM_TICK_PER_UPDATE_RATIO = 0.01

# Graphical stuff
NIGHT_OPACITY = 150

CROSSHAIR_ONLY_WITH_JOYSTICK = False
CROSSHAIR_SIZE = 10
CROSSHAIR_COLOR = (255, 255, 255)
CROSSHAIR_THICKNESS = 2

SLOT_BACKGROUND = (48, 29, 29)
SLOT_BACKGROUND_SELECTED = (88, 59, 59)

ITEM_SLOT_ITEM_SIZE = 64
ITEM_SLOT_PADDING = 8
ITEM_SLOT_MARGIN = 8
ITEM_SLOT_BORDER_RADIUS = 8

TOOLTIP_BACKGROUND_COLOR = (0, 0, 0)
TOOLTIP_PADDING = 5
TOOLTIP_WINDOW_MARGIN = 20
TOOLTIP_BORDER_RADIUS = 8
TOOLTIP_LINE_SPACING = -2

# Must match the assets in assets/ui... a bit hacky, but it works for now
NON_INTERACTABLE_SELECTION_COLOR = 'yellow'
INTERACTABLE_SELECTION_COLOR = 'green'
NOTHING_SELECTION_COLOR = 'gray'