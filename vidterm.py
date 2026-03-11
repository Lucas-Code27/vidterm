from pathlib import Path
from cv2 import VideoCapture, CAP_PROP_FPS, CAP_PROP_FRAME_COUNT
from logging import error
from queue import Queue
from threading import Thread
from sys import argv

from watch import watch_video
from producer import produce_frames
from config import get_config

def main():
    file_found = False
    video_path = None
    speed_scale = 1.0

    for i in range(len(argv) - 1):
        if argv[i] == "--file":
            file_found = True

            if Path(argv[i + 1]).is_file():
                video_path = argv[i + 1]

            if video_path == None:
                print(argv[i + 1])
                print("File not found")
                return
        elif argv[i] == "--speed":
            if float(argv[i + 1]):
                speed_scale = float(argv[i + 1])
            else:
                speed_scale = int(argv[i + 1])

            if speed_scale <= 0:
                print("Speed cannot be less than 0. Defaulting to 1.0 speed")
    
    if not file_found:
        print("You need to provide a path and the --path argument before it for the video file you want to play.")
        print("Example usage: <python path> <vidterm path> --path <video path>")
        print("pyinstaller version: <path to vidterm executable> --path <video path>")
        return

    video = VideoCapture(video_path) # type: ignore

    if not video.isOpened():
        print("File given is not a valid video and could not be openned by OpenCV2 please try again or use a different file")
        return

    frame_count = int(video.get(CAP_PROP_FRAME_COUNT))
    video_fps = video.get(CAP_PROP_FPS)
    video.release()

    conf = get_config()

    frame_buffer: Queue[str] = Queue(maxsize=conf["buffer_size"])
    preload_buffer_amount = conf["pre_load_buffer"]

    producer_thread = Thread(target=produce_frames, args=[frame_buffer, video_path], daemon=True)
    watch_thread = Thread(target=watch_video, args=[frame_buffer, video_fps, frame_count, preload_buffer_amount, speed_scale], daemon=True)
    
    try:
        print("\033[?25l")
        producer_thread.start()
        watch_thread.start()

        producer_thread.join()
        watch_thread.join()
    except KeyboardInterrupt:
        print("\033[?25h")
        exit()
    finally:
        print("\033[?25h")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        error("Hello my name is Error", exc_info=e, stack_info=True)