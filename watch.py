from os import system, get_terminal_size
from sys import stdout, getsizeof
from time import sleep, time
from queue import Queue, Empty
from re import compile

def watch_video(frame_buffer, video_fps, frame_count, preload_buffer_amount, speed_scale, debug):
    adjusted_fps = video_fps * speed_scale
    FRAME_DELAY = 1.0 / adjusted_fps

    ansi_escape = compile(r'\033\[[0-9;]*m')
    last_width = 0

    played_frames = 0

    last_frame = ""
    last_frame_width = 0
    last_padding = 0

    print("Loading...")

    if preload_buffer_amount > frame_count:
        while frame_buffer.qsize() < frame_count:
            sleep(10 / 1000)
    else:
        while frame_buffer.qsize() < preload_buffer_amount:
            sleep(10 / 1000)

    #print("\033[?25l")

    while True:
        try:
            frame = frame_buffer.get(timeout=1)
        except Empty:
            return
        except Exception as e:
            print(e)
            return

        try:
            term_width = get_terminal_size().columns
            if term_width != last_width:
                system("clear")
                last_width = term_width
        except:
            term_width = 80


        lines = frame.splitlines()

        frame_width = max(len(ansi_escape.sub("", line)) for line in lines) if lines else 0

        padding = max(0, (term_width - frame_width) // 2)

        padded_frame = "\n".join((" " * padding) + line + "\033[0m" for line in lines)

        if frame == "DUPE":
            render_start_time = time()

            stdout.write(f"\033[0;0H")
            stdout.write(last_frame + "\033[0m")

            played_frames += 1

            render_end_time = time()
            render_time = render_end_time - render_start_time

            played_ratio = played_frames / frame_count
            buffered_ratio = (played_frames + frame_buffer.qsize()) / frame_count

            played_chars = int(played_ratio * last_frame_width)
            buffer_chars = int(buffered_ratio * last_frame_width)

            stdout.write("\n\n" + (" " * last_padding))
            for i in range(last_frame_width):
                if i < played_chars:
                    stdout.write("█")
                elif i < buffer_chars:
                    stdout.write("▒")
                else:
                    stdout.write("░")
            stdout.write("\n")

            if debug:
                stdout.write("\n")
                stdout.write(f"Frame render time: {render_time:.6f}" + (" " * 12) + "\n")
                stdout.write(f"Frame Size: {round(getsizeof(frame)/1000, 3)} kilobytes" + (" " * 12) + "\n")
                stdout.write(f"Buffer: {frame_buffer.qsize()}/{frame_buffer.maxsize}" + (" " * 12) + "\n")

            stdout.flush()

            sleep_time = max(0, FRAME_DELAY - render_time)
            if sleep_time > 0:
                sleep(sleep_time)
            
            continue
            

        last_frame = padded_frame
        last_frame_width = frame_width
        last_padding = padding

        render_start_time = time()

        stdout.write(f"\033[0;0H")
        stdout.write(padded_frame + "\033[0m")

        played_frames += 1

        render_end_time = time()
        render_time = render_end_time - render_start_time

        played_ratio = played_frames / frame_count
        buffered_ratio = (played_frames + frame_buffer.qsize()) / frame_count

        played_chars = int(played_ratio * frame_width)
        buffer_chars = int(buffered_ratio * frame_width)

        stdout.write("\n\n" + (" " * padding))
        for i in range(frame_width):
            if i < played_chars:
                stdout.write("█")
            elif i < buffer_chars:
                stdout.write("▒")
            else:
                stdout.write("░")
        stdout.write("\n")

        if debug:
            stdout.write("\n")
            stdout.write(f"Frame render time: {render_time:.6f}" + (" " * 12) + "\n")
            stdout.write(f"Frame Size: {round(getsizeof(frame)/1000, 3)} kilobytes" + (" " * 12) + "\n")
            stdout.write(f"Buffer: {frame_buffer.qsize()}/{frame_buffer.maxsize}" + (" " * 12) + "\n")

        stdout.flush()

        sleep_time = max(0, FRAME_DELAY - render_time)
        if sleep_time > 0:
            sleep(sleep_time)

    #print("\033[?25h")
    #system("clear")