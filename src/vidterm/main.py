import sys
import time
from pathlib import Path
from typing import Generator

import ffmpeg
import numpy as np

def print_example_usage() -> None:
    print("Usage: vidterm <VIDEO_PATH> [args...]")

def stream_frames(video_path: str, width: int, height: int) -> Generator[np.ndarray, None, None]:
    frame_size = width * height

    process = (
        ffmpeg.input(str(video_path))
        .output("pipe:", format="rawvideo", pix_fmt="gray")
        .run_async(pipe_stdout=True, pipe_stderr=True)
    )

    try:
        while True:
            in_bytes = process.stdout.read(frame_size)
            if len(in_bytes) < frame_size:
                break
            
            frame = np.frombuffer(in_bytes, dtype=np.uint8).reshape((height, width))
            yield frame
    finally:
        process.stdout.close()
        if process.stderr:
            process.stderr.close()
        process.wait()

def main() -> None:
    # Get the video file from args
    file_path: Path = Path(sys.argv[1])

    # Make sure the file is in fact made out of file
    if not file_path.is_file():
        print("File provided was not a valid file or no path was provided")
        print_example_usage()

    # Probe the video
    try:
        probe = ffmpeg.probe(file_path)
    except ffmpeg.Error as e:
        print(f"Failed to probe video file: {e.stderr.decode()}")
        exit(1)

    # Get the first stream with video in the file
    video_stream = next(
        (stream for stream in probe["streams"] if stream["codec_type"] == "video"),
        None,
    )

    if video_stream is None:
        raise ValueError("No video stream found in the file")

    # Get per frame time delay
    frame_delay = 1 / int(video_stream["avg_frame_rate"].split("/")[0])

    # Get video size info
    width = int(video_stream["width"])
    height = int(video_stream["height"])

    char_list = [" ", "░", "▒", "▓", "█"]
    char_step = 255 // (len(char_list) - 1)

    try:
        for frame_idx, frame in enumerate(stream_frames(str(file_path), width, height)):
            print("\033[0:0H", end="")

            lines = []
            for row in frame[::2]:
                line = ""
                for pixel in row:
                    line += char_list[pixel // char_step]
                lines.append(line)

            print("\n".join(lines), end="")
            time.sleep(frame_delay)
                    
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        exit(1)
