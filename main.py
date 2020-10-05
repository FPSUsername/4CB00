#! /usr/bin/env python3
import rawpy
import matplotlib.pyplot as plt
import numpy as np
import os.path
import imageio
import threading

"""
Reads a RAW image file using rawpy
Returns the input file name, bayer image and RGB image
"""
def read_file():
    file_name = input("File name: ")
    if not os.path.isfile(file_name):
        print ("File does not exist")
        raise SystemExit
    print("{} loaded".format(file_name))

    raw = rawpy.imread(file_name)
    bayer = raw.raw_image
    rgb = raw.postprocess()

    print("Bayer data type: {}\tshape: {}".format(bayer.dtype, bayer.shape))
    print("RGB data type: {}\tshape: {}".format(rgb.dtype, rgb.shape))
    file_name = os.path.splitext(file_name)[0]
    return file_name, bayer, rgb

"""
Compress each color of an image (RGB)
Accepts a 2D array
"""
def compress(color):
    ahat = np.fft.rfft2(color)
    # Compress by throwing away low frequencies!

    # print("Run FFT")
    # M = im.shape[0]//R  # Rows
    # print("Input data type: {}\tshape: {}".format(im.dtype, im.shape))
    # # print("Input:\n{}".format(im))

    # print("FFT...")
    # ahat = np.fft.rfftn(im, s=(len(im), len(im[0]), 3))
    # print("FFT shape:{}".format(ahat.shape))

    # print("Stripping data...")
    # c_ahat = ahat[0:M] # Strip the FFT rows
    # print("Compressed FFT shape:{}".format(c_ahat.shape))

    # # Create zero array and insert the compressed array in zero array
    # print("Zero padding...")
    # c_ahat_p = np.zeros(ahat.shape, dtype=complex)
    # c_ahat_p[:c_ahat.shape[0],:c_ahat.shape[1]] = c_ahat
    # print("Zero padded FFT shape:{}".format(c_ahat_p.shape))

    # print("IFFT...")
    # result = np.fft.irfftn(c_ahat_p, s=(len(c_ahat_p), len(c_ahat_p[0]), 3)).astype(np.uint8)
    # print("Output data type: {} shape: {}".format(result.dtype, result.shape))

    result = np.fft.irfft2(ahat).astype(np.uint8)
    return result

"""
Split RGB, call compression function and reform the image.
Accepts a 3D array
"""
def compress_fft(ndarray_im):
    print("Compressing image")
    im = ndarray_im

    rgb = [im[:,:,0], im[:,:,1], im[:,:,2]]
    threads = []
    mydict = {}

    for index, color in enumerate(rgb):
        process = threading.Thread(target=lambda q, arg1: q.update({index: compress(arg1)}), args=(mydict, color))
        process.daemon = True
        process.start()
        threads.append(process)

    for process in threads:
        process.join()

    arrays = [mydict[0], mydict[1], mydict[2]]

    rgb_compressed = np.stack(arrays, axis=2)

    print("Image compressed")
    return rgb_compressed


def save_image(file_name, ndarray_image):
    print("Saving image")
    file_name = file_name + '_compressed.jpg'  # Set extension as jpg
    print("File saved as: {}".format(file_name))
    imageio.imwrite(file_name, ndarray_image)

if __name__ == '__main__':
    file_name, bayer, rgb = read_file()
    image = compress_fft(rgb)
    save_image(file_name, image)
