#! /usr/bin/env python3

import rawpy
import os.path

file_name = input("File name: ")
if not os.path.isfile(file_name):
    print ("File does not exist")
    raise SystemExit

raw = rawpy.imread(file_name)
bayer = raw.raw_image
rgb = raw.postprocess()

print(bayer.dtype, bayer.shape)
print(rgb.dtype, rgb.shape)
