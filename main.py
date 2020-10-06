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

    F = np.log(np.absolute(np.fft.fftshift(ahat)) + 1)

    thresh = 0.00001 * np.amax(np.absolute(ahat))
    ind = np.absolute(ahat)>thresh
    #ind = ind.transpose()
    ahatFilt = ahat*ind

    # count = ahat.size - ind.sum()
    # percent = 100-count/(ahat.size)*100

    result = np.fft.irfft2(ahatFilt).astype(np.uint8)
    return [result, F]

"""
Use Matplotlib to plot the frequencies of each color
Explects a dict where each value consists of a list,
where the second key, [1], is the array of the frequencies
"""
def plot_frequencies(rgb_comp):
    # Matplotlib render of the frequency domain
    rows = 1
    cols = len(rgb_comp.keys())
    axes=[]
    fig=plt.figure()

    plt.gray()
    for index, key in enumerate(rgb_comp):
        b = rgb_comp[key][1]
        axes.append( fig.add_subplot(rows, cols, index + 1) )
        subplot_title=(key + " frequencies")
        axes[-1].set_title(subplot_title)
        plt.imshow(b)
    fig.tight_layout()
    plt.show()

    return None

"""
Split RGB, call compression function and reform the image.
Accepts a 3D array
"""
def compress_fft(ndarray_im):
    print("Compressing image")
    im = ndarray_im

    rgb = {"Red": im[:,:,0], "Green": im[:,:,1], "Blue": im[:,:,2]}
    rgb_comp = {"Red": [], "Green": [], "Blue": []}  # Pre sorted
    threads = []

    for key, value in rgb.items():
        process = threading.Thread(target=lambda q, arg1: q.update({key: compress(arg1)}), args=(rgb_comp, value))
        process.daemon = True
        process.start()
        threads.append(process)

    for process in threads:
        process.join()

    answer = input("Do you want to see the frequency graphs? [y/n] ")
    if answer.lower() == "y":
        plot_frequencies(rgb_comp)

    arrays = [rgb_comp["Red"][0], rgb_comp["Green"][0], rgb_comp["Blue"][0]]
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
