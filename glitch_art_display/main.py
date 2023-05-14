#!/usr/bin/env python3

import os
import click
import hashlib
import imageio
from .jpeg import *
import subprocess as sp
from pathlib import Path
from contextlib import suppress
from multiprocessing import cpu_count

import concurrent.futures

cache_dir = Path.home() / '.cache/glitch-art-display'
cache_dir.mkdir(exist_ok=True)


frame_timings = [5, 4, 3, 2, 2, 1, 1, 1, 1]


def is_cached(filename):

    if (cache_dir / filename).is_file():
        return True
    return False


def find_images(directory):

    valid_suffixes = ['.jpg', '.jpeg']
    convert_suffixes = ['.png']

    for root,dirs,files in os.walk(directory):
        for file in files:
            filename = Path(root) / file

            # if image is a JPEG
            if any([filename.suffix.lower().endswith(s) for s in valid_suffixes]):
                yield filename

            # if image is an unsupported image type
            elif any([filename.suffix.lower().endswith(s) for s in convert_suffixes]):
                # try to convert it with imagemagick
                try:
                    new_filename = cache_dir / (filename.stem + '.jpg')
                    sp.run(['convert', str(filename), str(new_filename)], check=True)
                    yield new_filename
                except (FileNotFoundError, sp.CalledProcessError) as e:
                    print(f'[!] Unsupported file: {filename.name}')
                    print(f'[!]  - please install imagemagick in order to use {filename.suffix} files')


def gen_frames(image_dir, output, glitch_amount=100, fps=25, num_image_frames=25, num_transition_frames=30, shuffle=False):

    frame_groups = []
    frames_output = Path(output).resolve()
    frames_output.parent.mkdir(parents=True, exist_ok=True)
    frame_number = 0

    transition_frames = int(num_transition_frames/2)
    found_images = list(find_images(image_dir))
    if shuffle:
        random.shuffle(found_images)


    with concurrent.futures.ThreadPoolExecutor(max_workers=cpu_count()) as pool:
        for image in found_images:
            try:
                print(f'[+] Generating frames for {image.name}')

                glitched_frames = []

                image_bytes = bytearray(image.read_bytes())
                image_hash = hashlib.md5(image_bytes).hexdigest()
                png_filename = cache_dir / f'{image_hash}.png'
                if not png_filename.exists():
                    pool.submit(sp.run, ['convert', str(image), str(png_filename)], check=True)

                # generate glitch frames
                glitched_futures = []
                for i in range(transition_frames):
                    amount = int(glitch_amount * ((i+1)/transition_frames))
                    glitched_futures.append(pool.submit(glitch, image, amount, i))

                concurrent.futures.wait(glitched_futures)
                for glitched_future in glitched_futures:
                    glitched_frame = glitched_future.result()
                    if glitched_frame:
                        glitched_frames.append(glitched_frame)
            except KeyboardInterrupt:
                pool.shutdown(wait=False, cancel_futures=True)
                raise

            glitch_in = []
            random.shuffle(frame_timings)
            for i, glitched_image in enumerate(glitched_frames[::-1]):
                glitch_group = []
                for j in range(frame_timings[i % len(frame_timings)]):
                    glitch_group.append(glitched_image)
                glitch_in.append(glitch_group)

            normal = []
            for i in range(num_image_frames):
                normal.append(png_filename)

            glitch_out = []
            random.shuffle(frame_timings)
            for i, glitched_image in enumerate(glitched_frames):
                glitch_group = []
                for j in range(frame_timings[i % len(frame_timings)]):
                    glitch_group.append(glitched_image)
                glitch_out.append(glitch_group)

            frame_groups.append([glitch_in, normal, glitch_out])

    frames = []
    interlace_frames = max(2, min(int(transition_frames/4), 1))
    for i, [glitch_in, normal, glitch_out] in enumerate(frame_groups):
        for g in glitch_in:
            frames += g
        frames += normal
        if i == len(frame_groups)-1:
            for g in glitch_out:
                frames += g
        else:
            # truncate end of this glitch group
            glitch_out, glitch_interlaced = glitch_out[:-interlace_frames], glitch_out[-interlace_frames:]

            # truncate beginning of next glitch group
            frame_groups[i+1][0], glitch_next_interlaced = frame_groups[i+1][0][interlace_frames:], frame_groups[i+1][0][:interlace_frames]
            
            for g in glitch_out:
                frames += g
            for i in range(min(interlace_frames, len(glitch_interlaced))):
                frames += glitch_next_interlaced[i]
                frames += glitch_interlaced[i]

    w = imageio.get_writer(str(frames_output), format='FFMPEG', mode='I', fps=fps, macro_block_size=1)
    try:
        prev_frame = ''
        for i, frame in enumerate(frames):
            print(f'\r[+] Rendering frame {i:,}/{len(frames):,} ({i/len(frames)*100:.1f}%)', end='')
            frame = str(frame)
            if frame != prev_frame:
                try:
                    read_frame = imageio.imread(frame, pilmode='RGB')
                except Exception as e:
                    print(f'[!] Error reading {frame}: {e}')
                    continue
            try:
                w.append_data(read_frame)
            except ValueError:
                print(f'[!] {frame}')
                raise
            prev_frame = str(frame)
    finally:
        with suppress(Exception):
            w.close()

    print(f'[+] Video saved to {frames_output}')


def glitch(image, amount=None, sequence=''):

    print(f'[+] Glitching {image.name} by {amount}')

    if amount is None:
        amount = random.randint(0,99)
    else:
        amount = max(0, min(99, int(amount)-1))

    image = Path(image)

    image_bytes = bytearray(image.read_bytes())
    image_hash = hashlib.md5(image_bytes).hexdigest()
    try:
        jpeg = Jpeg(image_bytes)
    except JpegError as e:
        print(f'[!] {e}')
        return

    jpeg_filename = cache_dir / f'{image_hash}_{amount}_{sequence}.jpg'
    png_filename = cache_dir / f'{image_hash}_{amount}_{sequence}.png'

    print(f'[+] Glitching {image.name} by {amount}')

    # checked for cached files
    if is_cached(png_filename):
        print(f'[+] Found cached frame for {png_filename}')

    else:
        while 1:
            try:
                jpeg.amount      = amount
                jpeg.seed        = random.randint(0,99)
                jpeg.iterations  = max(0, min(115, int(amount*1.15)))

                # create a new image if not cached
                jpeg.save_image(jpeg_filename)
                try:
                    sp.run(['convert', str(jpeg_filename), str(png_filename)], check=True)
                    break
                except Exception:
                    continue

            except JpegError as e:
                print(f'[!] {e}')
                continue

    return png_filename


def main():
    @click.command(context_settings={'show_default': True})
    @click.argument('input', required=True, type=click.Path(exists=True, file_okay=False, dir_okay=True))
    @click.argument('output', required=True, type=click.Path(dir_okay=False))
    @click.option('--amount', default=50, type=click.IntRange(1, 100, clamp=True), help='Glitch amount')
    @click.option('--fps', default=25, type=float, help='Frames per second')
    @click.option('--normal-frames', default=25*25, type=int, help='Number of normal frames')
    @click.option('--transition-frames', default=30, type=int, help='Number of glitchy transition frames')
    @click.option('--dont-shuffle', is_flag=True, help='Don\'t shuffle order of images')
    def go(input, output, amount, fps, normal_frames, transition_frames, dont_shuffle):
        gen_frames(input, output, amount, fps, normal_frames, transition_frames, not dont_shuffle)

    try:
        go()
    except KeyboardInterrupt:
        print("Interrupted")

if __name__ == '__main__':
    main()