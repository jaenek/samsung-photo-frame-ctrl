#!/usr/bin/env python
import argparse
import os
import time
import signal
import sys
from tempfile import mkdtemp

from frame_ctrl import FrameController

TMP_PATH = mkdtemp()

parser  = argparse.ArgumentParser()
parser.add_argument('-i', '--interval', type=int, default=5, help='Image slideshow interval')
parser.add_argument('directory', type=str, help='Directory with images')
args = parser.parse_args()

cached_files = {}
def resize_image(filename, geometry):
    base_filename = os.path.basename(filename)
    if base_filename in cached_files:
        print(f'[INFO] {cached_files[base_filename]}')
        return cached_files[base_filename]
    else:
        print(f'[INFO] {filename}')

    cached_filename = os.path.join(TMP_PATH, os.path.splitext(base_filename)[0] + '.jpg')
    os.system(f'convert {filename} -resize {geometry} -background black -gravity center -extent {geometry} {cached_filename}')
    cached_files[base_filename] = cached_filename

    return cached_filename

frame_ctrl = FrameController()

try:
    while True:
        for filename in os.listdir(args.directory):
            filename = resize_image(os.path.join(args.directory, filename), frame_ctrl.get_display_geometry())
            frame_ctrl.write_image_from_file(filename)
            time.sleep(args.interval)
except KeyboardInterrupt:
    print('\nSlideshow ended')
    sys.exit()
