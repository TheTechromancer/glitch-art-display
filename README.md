# glitch-art-display
Art display with seizure-inducing glitch transitions.

https://user-images.githubusercontent.com/20261699/127774381-7aea0c09-d7f8-417d-9094-0578d211a160.mp4

## Installation
~~~
$ pip install git+https://github.com/thetechromancer/glitch-art-display
~~~

## Example
NOTE: All images must be the same resolution

NOTE: Frames in the `OUTPUT` directory are symlinks only, so they take up very little space.
~~~
# generate frames
$ glitch-art-display --shuffle ~/Pictures /tmp/ffmpeg_frames

# generate .MP4 from frames
$ ffmpeg -framerate 25 -i /tmp/ffmpeg_frames/frame_%09d.png output.mp4

# loop forever
$ vlc --loop --fullscreen --no-video-title-show output.mp4
~~~

## Usage
~~~
Usage: glitch-art-display [OPTIONS] INPUT OUTPUT

Options:
  --amount INTEGER RANGE       Glitch amount (1 to 100)
  --normal-frames INTEGER      Number of normal frames
  --transition-frames INTEGER  Number of glitchy transition frames
  --shuffle                    Shuffle order of images
  --help                       Show this message and exit.
~~~
