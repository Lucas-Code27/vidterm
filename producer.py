import numpy
import numpy.core.defchararray
import queue
import time
import cv2

import config

def frame_generator(path):
    cap = cv2.VideoCapture(filename=path)
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret: break
        yield frame
    cap.release()

def produce_frames(frame_buffer, video_path):
    #performance_times = {}

    TIMEOUT = 15
    MAX_TIMEOUT = 2000

    CHAR_SIZE_X = 1
    CHAR_SIZE_Y = 2

    frame_gen = frame_generator(video_path)
    image_frame_buffer = queue.Queue(maxsize=frame_buffer.maxsize)

    image_sleep_time = time.time()

    conf = config.get_config()
    quantization_level = conf["quantization_level"]
    black_point = conf["black_point"]

    char_x = CHAR_SIZE_X * quantization_level
    char_y = CHAR_SIZE_Y * quantization_level
    
    while True:
        if image_frame_buffer.full():
            if time.time() - image_sleep_time > MAX_TIMEOUT / 1000:
                raise Exception("YOU'RE TAKING TOO LONG")

            time.sleep(TIMEOUT / 1000)
        
        image_sleep_time = time.time()

        #start_time = time.time()

        try:
            file_frame = next(frame_gen)
        except StopIteration:
            return

        #end_time = time.time()
        #performance_times["get_image"] = end_time - start_time

        #start_time = time.time()

        pixels_grid = cv2.cvtColor(file_frame, cv2.COLOR_BGR2RGB)

        height = pixels_grid.shape[0]
        width = pixels_grid.shape[1]

        h2 = (height // char_y) * char_y
        w2 = (width // char_x) * char_x

        cropped = pixels_grid[:h2, :w2]

        blocks_y = h2 // char_y
        blocks_x = w2 // char_x

        reshaped = cropped.reshape(
            blocks_y, char_y,
            blocks_x, char_x,
            3
        )

        top_half = reshaped[:, :char_y // 2, :, :, :]
        bottom_half = reshaped[:, char_y // 2:, :, :, :]

        avg_color = numpy.mean(top_half, axis=(1, 3)).astype("uint8")
        bottom_avg_color = numpy.mean(bottom_half, axis=(1, 3)).astype("uint8")

        #end_time = time.time()

        #performance_times["prepare_image"] = end_time - start_time

        #start_time = time.time()

        black_point_mask = numpy.any(avg_color > black_point, axis=-1)

        red = avg_color[:, :, 0]
        green = avg_color[:, :, 1]
        blue = avg_color[:, :, 2]

        bottom_red = bottom_avg_color[:, :, 0]
        bottom_green = bottom_avg_color[:, :, 1]
        bottom_blue = bottom_avg_color[:, :, 2]

        chars = numpy.core.defchararray.add(
            numpy.core.defchararray.add(
                numpy.core.defchararray.add(
                    numpy.core.defchararray.add(
                        numpy.core.defchararray.add(
                            numpy.core.defchararray.add("\033[38;2;", red.astype(str)),
                            numpy.core.defchararray.add(";", green.astype(str))
                        ),
                        numpy.core.defchararray.add(";", blue.astype(str))
                    ),
                    "m"
                ),
                numpy.core.defchararray.add(
                    numpy.core.defchararray.add(
                        numpy.core.defchararray.add("\033[48;2;", bottom_red.astype(str)),
                        numpy.core.defchararray.add(";", bottom_green.astype(str))
                    ),
                    numpy.core.defchararray.add(";", bottom_blue.astype(str))
                )
            ),
            "m▀"
        )

        chars_array = numpy.where(black_point_mask, chars, ' \u001b[0m')

        lines_array = numpy.core.defchararray.add(chars_array, "")
        lines = ["".join(row) + "\n" for row in lines_array]

        frame_buffer.put("".join(lines))
        #end_time = time.time()

        #performance_times["convert_image_to_text"] = end_time - start_time

        #print("Buffer Performance: ", performance_times)