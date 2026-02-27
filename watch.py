from pathlib import Path
from tqdm import tqdm
import os
import time

frames_folder = "output/"

filenames = [str(f) for f in Path(frames_folder).glob("*.txt")]
sorted_filenames = sorted(filenames)

frames = []

for image_path in tqdm(sorted_filenames, desc="Preloading Frames"):
    with open(image_path, "r") as f:
        frames.append(f.read())

for frame in frames:
    print(frame)
    time.sleep(0.033)

os.system("clear")