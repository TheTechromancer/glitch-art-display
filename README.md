# glitch-art-display
Art display with seizure-inducing glitch transitions.

## Installation
~~~
$ pip install git+https://github.com/thetechromancer/glitch-art-display
~~~

## Example
NOTE: All images must be the same resolution
NOTE: Frames in the `OUTPUT` directory are symlinks only, so they take up very little space.
~~~
# generate frames
$ glitch-art-display --amount 75 ~/Pictures /tmp/ffmpeg_frames

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