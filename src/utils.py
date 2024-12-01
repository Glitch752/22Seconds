import sys
import platform

def lerp(a, b, t):
    return a + (b - a) * t

def clamp(x, mi, ma):
    return max(mi, min(x, ma))

def ease(t):
    return t * t * (3 - 2 * t)

def is_web() -> bool:
    return sys.platform == "emscripten" or 'wasm' in platform.machine()

def get_username():
    if is_web():
        return "Player"

    import os
    return os.getlogin()

def get_asset(*path: list[str]) -> str:
    if is_web():
        path: list[str] = list(path)
        filename = path[-1]
        if filename.endswith(".wav"):
            path[-1] = filename[:-4] + ".ogg"
        
        return "web_assets/" + "/".join(path)
    
    import os
    return os.path.join("assets", *path)