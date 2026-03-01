from PIL import Image
import io
import termcolor
import queue
import time
import cv2

import config

TIMEOUT = 15
MAX_TIMEOUT = 2000

def frame_generator(path):
    cap = cv2.VideoCapture(filename=path)
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret: break
        yield frame
    cap.release()

def produce_frames(frame_buffer):
    frame_gen = frame_generator("video/video.mp4")

    sleep_time = time.time()

    conf = config.get_config()
    quantization_level = conf["quantization_level"]

    image_frame_buffer = queue.Queue(maxsize=frame_buffer.maxsize)
    
    while True:
        if image_frame_buffer.full():
            if time.time() - sleep_time > MAX_TIMEOUT / 1000:
                raise Exception("YOU'RE TAKING TOO LONG")

            time.sleep(TIMEOUT / 1000)
        
        sleep_time = time.time()

        try:
            file_frame = next(frame_gen)
        except StopIteration:
            return

        encode_success, image = cv2.imencode(".png", file_frame)

        if not encode_success:
            raise Exception("Failed to encode frame")

        frame = image.tobytes()
        frame_bytes = io.BytesIO(frame)

        picture = Image.open(frame_bytes)
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
        frame_buffer.put(image_text_data)