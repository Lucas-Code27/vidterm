import os
import sys
import time
import queue
import re

def watch_video(frame_buffer, video_fps, frame_count, preload_buffer_amount, speed_scale):
    adjusted_fps = video_fps * speed_scale
    FRAME_DELAY = 1.0 / adjusted_fps

    ansi_escape = re.compile(r'\033\[[0-9;]*m')
    last_width = 0

    played_frames = 0

    print("Loading...")

    if preload_buffer_amount > frame_count:
        while frame_buffer.qsize() < frame_count:
            time.sleep(10 / 1000)
    else:
        while frame_buffer.qsize() < preload_buffer_amount:
            time.sleep(10 / 1000)

    #print("\033[?25l")

    while True:
        try:
            frame = frame_buffer.get(timeout=1)
        except queue.Empty:
            return
        except Exception as e:
            print(e)
            return

        try:
            term_width = os.get_terminal_size().columns
            if term_width != last_width:
                os.system("clear")
                last_width = term_width
        except:
            term_width = 80

        lines = frame.splitlines()

        frame_width = max(len(ansi_escape.sub("", line)) for line in lines) if lines else 0

        padding = max(0, (term_width - frame_width) // 2)

        padded_frame = "\n".join((" " * padding) + line + "\033[0m" for line in lines)

        render_start_time = time.time()

        sys.stdout.write(f"\033[0;0H")
        sys.stdout.write(padded_frame + "\033[0m")

        played_frames += 1

        render_end_time = time.time()
        render_time = render_end_time - render_start_time

        played_ratio = played_frames / frame_count
        buffered_ratio = (played_frames + frame_buffer.qsize()) / frame_count

        played_chars = int(played_ratio * frame_width)
        buffer_chars = int(buffered_ratio * frame_width)

        sys.stdout.write("\n\n" + (" " * padding))
        for i in range(frame_width):
            if i < played_chars:
                sys.stdout.write("█")
            elif i < buffer_chars:
                sys.stdout.write("▒")
            else:
                sys.stdout.write("░")
        sys.stdout.write("\n")

        #sys.stdout.write(f"{sys.getsizeof(frame)}\n") # frame data size check

        sys.stdout.flush()

        #print("\n" + (" " * padding) + f"Buffer: {frame_buffer.qsize()}/{frame_buffer.maxsize}      ")
        #print("Time to render frame: ", render_time)

        sleep_time = max(0, FRAME_DELAY - render_time)
        if sleep_time > 0:
            time.sleep(sleep_time)

    #print("\033[?25h")
    #os.system("clear")