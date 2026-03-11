# Vidterm
#### A simple video player for the terminal

## Features
- Multi-Threaded buffering and rendering
- Supports any video format that OpenCV2 supports
- Color

## Planned Features
- Audio
- Playback controls (Pause/Resume)

## Dependencies
- numpy
- opencv-python

# How to use

## Installation
- Clone the repo `git clone https://github.com/Lucas-Code27/vidterm.git`
- Download the dependencies in a python virtual environment
- Run the vidterm.py script with the required arguments

## How to run
`<Virtual envirnment python executable> <path to vidterm.py> --path <video file>`

Optional Arguments:
- `--speed <int or float value above 0>` Changes the video playback speed
- `--debug` Displays debug information about renderer and buffer performance
