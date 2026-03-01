import logging
from PIL import Image
from pathlib import Path
from tqdm import tqdm
import termcolor
import json
import io
import queue
import threading

import watch
import producer

BUFFER_SIZE = 100

def main():
    frame_buffer = queue.Queue(maxsize=BUFFER_SIZE)

    producer_thread = threading.Thread(target=producer.produce_frames, args=[frame_buffer])

    watch_thread = threading.Thread(target=watch.watch_video, args=[frame_buffer])

    producer_thread.start()
    watch_thread.start()

    producer_thread.join()
    watch_thread.join()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.error("Hello my name is Error", exc_info=e, stack_info=True)