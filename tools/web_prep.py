import os, sys, shutil
from pydub import AudioSegment

import glob
from os import path

lc = lambda x: len(open(x).readlines())

base_assets = path.normpath(path.join(path.dirname(__file__), "..", "assets"))
pattern = base_assets + '/**/*'
web_assets_path = path.normpath(path.join(path.dirname(__file__), "..", "src", "web_assets"))

for file in glob.glob(pattern, recursive=True):
    extension = path.splitext(file)[1]
    if extension not in [".wav", ".png", ".ttf"]:
        continue
    
    if extension == ".wav":
        new_path = path.join(web_assets_path, path.relpath(file, base_assets))
        new_path = new_path[:-4] + ".ogg"
        if os.path.exists(new_path):
            continue
        
        print(f"Converting {file} to {new_path}")
        audio_segment = AudioSegment.from_wav(file)
        os.makedirs(path.dirname(new_path), exist_ok=True)
        audio_segment.export(new_path, format="ogg")
    else:
        new_path = path.join(web_assets_path, path.relpath(file, base_assets))
        if os.path.exists(new_path):
            continue
        
        print(f"Copying {file} to {new_path}")
        os.makedirs(path.dirname(new_path), exist_ok=True)
        shutil.copy(file, new_path)