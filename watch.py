from pathlib import Path
from tqdm import tqdm
import termcolor
import os
import sys
import time
import queue

def watch_video(frame_buffer):
    FPS = 30
    FRAME_DELAY = 1 / FPS

    next_frame_time = time.perf_counter()

    print("Loading...")

    while frame_buffer.qsize() < frame_buffer.maxsize / 2:
        time.sleep(10 / 1000)

    #print("\033[?25l")
    os.system("clear")

    while True:
        try:
            frame = frame_buffer.get(timeout=1)
        except queue.Empty:
            return

        sys.stdout.write("\033[0;0H")
        sys.stdout.write(frame)
        sys.stdout.flush()

        next_frame_time += FRAME_DELAY
        sleep_time = next_frame_time - time.perf_counter()
        if sleep_time > 0:
            time.sleep(FRAME_DELAY)

    #print("\033[?25h")
    #os.system("clear")