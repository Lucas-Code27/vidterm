import os
import sys
import time
import queue

def watch_video(frame_buffer, video_fps, frame_count):
    FRAME_DELAY = 1.0 / video_fps

    print("Loading...")

    if frame_buffer.maxsize / 2 > frame_count:
        while frame_buffer.qsize() < frame_count:
            time.sleep(10 / 1000)
    else:
        while frame_buffer.qsize() < frame_buffer.maxsize / 2:
            time.sleep(10 / 1000)

    #print("\033[?25l")
    os.system("clear")

    while True:
        try:
            frame = frame_buffer.get(timeout=1)
        except queue.Empty:
            return
        except Exception as e:
            print(e)
            return

        render_start_time = time.time()

        sys.stdout.write("\033[0;0H\u001b[40m")
        sys.stdout.write(frame + "\033[0m")
        sys.stdout.flush()

        render_end_time = time.time()
        render_time = render_end_time - render_start_time

        print(f"Buffer: {frame_buffer.qsize()}/{frame_buffer.maxsize}     ")
        #print("Time to render frame: ", render_time)

        sleep_time = max(0, FRAME_DELAY - render_time)
        if sleep_time > 0:
            time.sleep(sleep_time)

    #print("\033[?25h")
    #os.system("clear")