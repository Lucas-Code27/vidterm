import logging
from PIL import Image
from pathlib import Path
from tqdm import tqdm
import termcolor
import json
import io

import vid2img
import watch

def main():
    quantization_level = 8

    try:
        with open('config/config.json', 'r') as f:
            data = json.load(f)

            quantization_level = data["quantization-level"]
    except Exception as e:
        print(f"Config loading had an error! {e}")

        quantization_level = 8

    FRAME_COUNT = -1

    image_frames = vid2img.convert_video_to_images("video/video.mp4", FRAME_COUNT)
    text_frames = []

    print("CONVERTING TO TEXT FILES")

    for image in tqdm(image_frames, "Converting"):
        frame = image.tobytes()
        frame_buffer = io.BytesIO(frame)

        picture = Image.open(frame_buffer)
        gs_picture = picture

        picture = picture.convert("RGB")
        gs_picture = gs_picture.convert("L")

        width, height = picture.size

        # Load the pixel data for efficient access
        pixels = picture.load()
        lum_pixels = gs_picture.load()

        image_text_data = ""

        # Loop over all pixels
        for y in range(height):
            if y % (quantization_level * 2) != 0: continue
            line = ""

            for x in range(width):
                if (quantization_level > 1):
                    if x % quantization_level != 0: continue

                red, green, blue = pixels[x, y]
                value = lum_pixels[x, y]
                color = (red, green, blue)

                if value > 180:
                    line += termcolor.colored('█', color)
                elif value > 128:
                    line += termcolor.colored('▓', color)
                elif value > 64:
                    line += termcolor.colored('▒', color)
                elif value > 32:
                    line += termcolor.colored('░', color)
                else:
                    line += ' '
            image_text_data += line + "\n"
        text_frames.append(image_text_data)

    watch.watch_video(text_frames)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.error("Hello my name is Error", exc_info=e, stack_info=True)