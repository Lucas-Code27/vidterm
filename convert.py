from PIL import Image
from pathlib import Path
from tqdm import tqdm
import json

import vid2img

quantization_level = 1

try:
    with open('config/config.json', 'r') as f:
        data = json.load(f)

        quantization_level = data["quantization-level"]
except Exception as e:
    print(f"Config loading had an error! {e}")

    quantization_level = 1


frames_folder = "frames/"
output_folder = "output/"

# Todo: Figure out how to get arguments working
#print("Converting Video into Images")
#
#video_filenames = [Path(f) for f in Path(frames_folder).glob("*.mp4")]
#
#if not vid2img.convert_video_to_images("video/video.mp4"):
#    print("Failed to convert video to images")
#else:
#    print("Converted Video to Images!")

frame_filenames = [Path(f) for f in Path(frames_folder).glob("*.png")]

print("CONVERTING TO TEXT FILES")

for image_path in tqdm(frame_filenames, "Converting"):
    picture = Image.open(image_path)

    picture = picture.convert("L")

    width, height = picture.size

    # Load the pixel data for efficient access
    pixels = picture.load()

    image_text_data = []

    # Loop over all pixels
    for y in range(height):
        if y % (quantization_level * 2) != 0: continue
        line = ""

        for x in range(width):
            if (quantization_level > 1):
                if x % quantization_level != 0: continue

            value = pixels[x, y]

            if value > 180:
                line += '█'
            elif value > 128:
                line += '▓'
            elif value > 64:
                line += '▒'
            elif value > 32:
                line += '░'
            else:
                line += ' '
        image_text_data.append(line)

    with open(output_folder + image_path.stem + ".txt", 'w') as file:
        for line in image_text_data:
            file.write(line + '\n')

print("Convertion Complete!")