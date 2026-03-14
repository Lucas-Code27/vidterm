from pathlib import Path
from logging import error
from queue import Queue
from threading import Thread
from sys import argv, exit
import ffmpeg

from watch import watch_video
from producer import produce_frames
from config import get_config

def main():
    file_found = False
    video_path = None
    speed_scale = 1.0
    debug = False
    video_mode = "truecolor"

    for i in range(len(argv)):
        if argv[i] == "--path":
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
        elif argv[i] == "--debug":
            debug = True
        elif argv[i] == "--no-color":
            video_mode = "gs"
    
    if not file_found:
        print("You need to provide a path and the --path argument before it for the video file you want to play.")
        print("Example usage: <python path> <vidterm path> --path <video path>")
        print("pyinstaller version: <path to vidterm executable> --path <video path>")
        return

    try:
        probe = ffmpeg.probe(video_path)
        stream = next((s for s in probe['streams'] if s['codec_type'] == 'video'), None)

        if stream is None:
            print("Failed to laod video stream")
            exit(1)
        
        fps_str = stream.get("avg_frame_rate", "0/1")
        try:
            video_fps = eval(fps_str)
        except ZeroDivisionError:
            print("fps was divided by zero")
            exit(1)
        
        if video_fps == 0:
            print("video fps detected as 0 aborting")
            exit(1)

        frame_count = int(stream.get("nb_frames", 0))

        if frame_count == 0:
            duration = float(stream.get("duration", 0))

            if duration == 0:
                print("Video is so short it doesn't exist (This is sometimes caused by the file format .mp4 is recommended)")
                exit(1)

            frame_count = int(duration * video_fps)
    except ffmpeg.Error:
        print("Failed to load video metadata")
        exit(1)

    if frame_count == 0:
        print("Failed to get a proper frame count")
        exit(1)

    conf = get_config()

    if video_mode != "gs" and video_mode != "truecolor":
        print("Unknown color mode")
        exit(1)

    frame_buffer: Queue[str] = Queue(maxsize=conf["buffer_size"])
    preload_buffer_amount = conf["pre_load_buffer"]

    producer_thread = Thread(target=produce_frames, args=[frame_buffer, video_path, debug, video_mode], daemon=True)
    watch_thread = Thread(target=watch_video, args=[frame_buffer, video_fps, frame_count, preload_buffer_amount, speed_scale, debug], daemon=True)
    
    try:
        print("\033[?25l")
        producer_thread.start()
        watch_thread.start()

        producer_thread.join()
        watch_thread.join()
    except KeyboardInterrupt:
        print("\033[?25h")
        exit(1)
    finally:
        print("\033[?25h")
        exit(0)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        error("Hello my name is Error", exc_info=e, stack_info=True)
        exit(1)