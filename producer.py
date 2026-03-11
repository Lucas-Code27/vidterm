from numpy import any, where, roll, full
from numpy.core import defchararray
from queue import Queue
from time import time, sleep
from cv2 import VideoCapture

from config import get_config

def frame_generator(path):
    cap = VideoCapture(filename=path)
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret: break
        yield frame
    cap.release()

def produce_frames(frame_buffer, video_path, debug):
    performance_times = {}

    TIMEOUT = 15
    MAX_TIMEOUT = 2000

    DEBUG_ROUND_DIGITS = 3

    CHAR_SIZE_X = 1
    CHAR_SIZE_Y = 2

    frame_gen = frame_generator(video_path)
    image_frame_buffer = Queue(maxsize=frame_buffer.maxsize)

    image_sleep_time = time()

    conf = get_config()
    quantization_level = conf["quantization_level"]

    char_x = CHAR_SIZE_X * quantization_level
    char_y = CHAR_SIZE_Y * quantization_level
    
    while True:
        if image_frame_buffer.full():
            if time() - image_sleep_time > MAX_TIMEOUT / 1000:
                raise Exception("YOU'RE TAKING TOO LONG")

            sleep(TIMEOUT / 1000)
        
        image_sleep_time = time()
        
        start_time = time()

        try:
            file_frame = next(frame_gen)
        except StopIteration:
            return

        if debug:
            end_time = time()
            performance_times["get_image"] = round(end_time - start_time, DEBUG_ROUND_DIGITS)
            start_time = time()

        height = file_frame.shape[0]
        width = file_frame.shape[1]

        h2 = (height // char_y) * char_y
        w2 = (width // char_x) * char_x

        cropped = file_frame[:h2, :w2]

        blocks_y = h2 // char_y
        blocks_x = w2 // char_x

        reshaped = cropped.reshape(
            blocks_y, char_y,
            blocks_x, char_x,
            3
        )

        half = char_y // 2

        top_half = reshaped[:, :half].mean(axis=(1, 3)).astype("uint8")
        bottom_half = reshaped[:, half:].mean(axis=(1, 3)).astype("uint8")

        fg = top_half
        bg = bottom_half

        fg_prev = roll(fg, 1, axis=1)
        bg_prev = roll(bg, 1, axis=1)

        fg_prev[:, 0] = 255
        bg_prev[:, 0] = 0

        change_mask = any((fg != fg_prev) | (bg != bg_prev), axis=2)

        if debug:
            end_time = time()
            performance_times["prepare_image"] = round(end_time - start_time, DEBUG_ROUND_DIGITS)
            start_time = time()

        colors = defchararray.add(
            defchararray.add(
                defchararray.add(
                    defchararray.add(
                        defchararray.add(
                            defchararray.add("\033[38;2;", fg[:, :, 2].astype(str)),
                            defchararray.add(";", fg[:, :, 1].astype(str))
                        ),
                        defchararray.add(";", fg[:, :, 0].astype(str))
                    ),
                    "m"
                ),
                defchararray.add(
                    defchararray.add(
                        defchararray.add("\033[48;2;", bg[:, :, 2].astype(str)),
                        defchararray.add(";", bg[:, :, 1].astype(str))
                    ),
                    defchararray.add(";", bg[:, :, 0].astype(str))
                )
            ),
            "m"
        )

        chars = full(fg[:, :, 2].shape, "▀", dtype="<U32")

        chars = where(change_mask, defchararray.add(colors, chars), chars)

        end_time = time()

        if debug:
            performance_times["convert_image_to_text"] = round(end_time - start_time, DEBUG_ROUND_DIGITS)
            performance_times["total"] = round(performance_times["convert_image_to_text"] + performance_times["get_image"] + performance_times["prepare_image"], DEBUG_ROUND_DIGITS)

        lines_array = defchararray.add(chars, "")
        lines = ["".join(row) + "\n" for row in lines_array]

        if debug:
            lines.append(f"Buffer Times: {performance_times}    ")

        frame_buffer.put("".join(lines))