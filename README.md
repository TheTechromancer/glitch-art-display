# glitch-art-display
Art display with seizure-inducing glitch transitions.

https://user-images.githubusercontent.com/20261699/127774463-903d5583-5281-4187-ba1e-d2a44b14e9c0.mp4

## Installation
~~~bash
pipx install git+https://github.com/thetechromancer/glitch-art-display
~~~

## Example
NOTE: All images must be the same resolution
~~~bash
# generate .MP4
glitch-art-display ~/Pictures ./output.mp4

# play the video and loop forever
vlc --loop --fullscreen --no-video-title-show output.mp4
~~~

## Usage
~~~bash
glitch-art-display --help
Usage: glitch-art-display [OPTIONS] INPUT OUTPUT

Options:
  --amount INTEGER RANGE       Glitch amount  [default: 50; 1<=x<=100]
  --fps FLOAT                  Frames per second  [default: 25]
  --normal-frames INTEGER      Number of normal frames  [default: 625]
  --transition-frames INTEGER  Number of glitchy transition frames  [default:
                               30]
  --dont-shuffle               Don't shuffle order of images  [default: False]
  --help                       Show this message and exit.  [default: False]
~~~
