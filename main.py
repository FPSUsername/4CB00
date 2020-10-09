#! /usr/bin/env python3
import rawpy
import matplotlib.pyplot as plt
import numpy as np
import os.path
import imageio
import threading

"""
Reads a RAW image file using rawpy

:returns: input file name
:returns: numpy 3D array of RGB image
"""
def read_raw_file():
    file_name = input("File name: ")
    if not os.path.isfile(file_name):
        print ("File does not exist")
        raise SystemExit
    print("{} loaded".format(file_name))

    raw = rawpy.imread(file_name)
    # bayer = raw.raw_image
    rgb = raw.postprocess()

    # print("Bayer data type: {}\tshape: {}".format(bayer.dtype, bayer.shape))
    print("RGB data type: {}\tshape: {}".format(rgb.dtype, rgb.shape))
    file_name = os.path.splitext(file_name)[0]
    return file_name, rgb  #, bayer

"""
Reads a FFT image file

Returns the 3D array
:returns: file name
:returns: list of ndarray's (RGB)
:returns: original file shape
"""
def read_fft_file():
    file_name = input("File name: ")
    if not os.path.isfile(file_name):
        print ("File does not exist")
        raise SystemExit

    rgb_fft = np.load(file_name, allow_pickle=True)

    rgb_fft_shape = rgb_fft["arr_0"][0]
    rgb_fft_im = rgb_fft["arr_0"][1]

    file_name = os.path.splitext(file_name)[0]
    return file_name, rgb_fft_im, rgb_fft_shape

"""
Use Matplotlib to plot the frequencies of each color

:param: dict where each value consists of a list of which the second key, [1], is the array of the frequencies
"""
def plot_frequencies(rgb_comp):
    # Matplotlib render of the frequency domain
    rows = 1
    cols = len(rgb_comp)
    axes=[]
    fig=plt.figure()

    plt.gray()
    # R G B
    for index, key in enumerate(rgb_comp):
        b = rgb_comp[key][2]
        axes.append( fig.add_subplot(rows, cols, index + 1) )
        subplot_title=(key + " frequencies")
        axes[-1].set_title(subplot_title)
        plt.imshow(b)

    fig.tight_layout()
    plt.show()

"""
Trim the leading and trailing zeros from a N-D array.

:param: numpy array
:param: how many zeros to leave as a margin
:returns: trimmed array
:returns: slice object
"""
def trim_zeros(arr, margin=0):
    s = []
    for dim in range(arr.ndim):
        start = 0
        end = -1
        slice_ = [slice(None)]*arr.ndim

        # go = True
        # while go:
        #     slice_[dim] = start
        #     go = not np.any(arr[tuple(slice_)])
        #     start += 1
        # start = max(start-1-margin, 0)

        go = True
        while go:
            slice_[dim] = end
            go = not np.any(arr[tuple(slice_)])
            end -= 1
        end = arr.shape[dim] + min(-1, end+1+margin) + 1

        s.append(slice(start,end))
    return arr[tuple(s)]#, tuple(s)

"""
Compress a 2D array using FFT

:param: numpy 2D array
:param: compression number [0, 100]
:returns: list of Compressed FFT, Compressed FFT in reduced form, Frequencies, Compression percentage (FFT)
"""
def compress(color, compression):
    ahat = np.fft.rfft2(color)
    # Compress by throwing away low frequencies!
    F = np.log(np.absolute(np.fft.fftshift(ahat)) + 1)  # Frequencies in human readable form

    val = 0.000004 * compression  # From 0 to 4e-4
    thresh = val * np.amax(np.absolute(ahat))
    ind = np.absolute(ahat)>thresh  # Matrix filled with True and False
    ahatFilt = np.multiply(ahat, ind)  # Element wise multiplication
    ahatFilt_reduced = trim_zeros(ahatFilt)

    count = ahat.size - np.sum(ind)  # Total number of nonzero Fourier coëfficients
    percent = 100 - count / (ahat.size) * 100  # Percentage kept in terms of FFT
    # comp_percent = compression + percent

    return [ahatFilt, ahatFilt_reduced, F, percent]

"""
Decompress a FFT 2D array

:param: numpy 2D array (rfft2)
:return: numpy 2D array (irfft2)
"""
def decompress(color):
    Afilt = np.fft.irfft2(color)
    return Afilt

"""
Compress image using FFT

:param: numpy 3D array
:returns: list of R, G, B numpy 2D arrays
:returns: list of image shape
:returns: compression percentage
"""
def compress_fft(rgb):
    print("Compressing image")
    im = rgb

    # Set compression
    compression = input("Compress amount [0, 100]: ")

    while True:
        try:
            compression = int(compression)
            if compression < 0:
                compression = 0
            elif compression > 100:
                compression = 100
            break
        except:
            if compression.lower() == "q":
                raise SystemExit
            compression = input("Incorrect input parameter, try again. (press q to quit) ")

    # Split R G and B into the dict 'rgb'
    # Create a dict 'rgb_info', which is pre sorted, that will contain the ifft and compressed irfft data
    rgb = {"Red": im[:,:,0], "Green": im[:,:,1], "Blue": im[:,:,2]}
    rgb_info = {"Red": [], "Green": [], "Blue": []}
    rgb_array_fft = []
    rgb_array_fft_r = []
    threads = []

    # Compute
    for key, value in rgb.items():
        process = threading.Thread(target=lambda q, arg1, arg2: q.update({key: compress(arg1, arg2)}), args=(rgb_info, value, compression))
        process.daemon = True
        process.start()
        threads.append(process)

    # Wait for all tasks to finish
    for process in threads:
        process.join()

    # Create the full compressed image
    for value in rgb_info.values():
        rgb_array_fft.append(value[0])  # Complex, ahat
        rgb_array_fft_r.append(value[1])  # Complex, ahat reduced (different sizes!)

    rgb_fft = np.stack(rgb_array_fft, axis=2)

    # Show plots of each frequency
    answer = input("Check frequency graphs? [y/n] ")
    if answer.lower() == "y":
        plot_frequencies(rgb_info)

    print("Image compressed")
    return rgb_array_fft_r, rgb_fft.shape, compression

"""
Decompress FFT image

:param: list consists of ndarrays in rfft2 form
:param: list complete image shape
:returns: numpy 3D array
"""
def decompress_fft(rgb_fft, rgb_fft_full_shape):
    print("Deompressing image")

    # Zero padding
    for index, value in enumerate(rgb_fft):
        zeros_to_add = rgb_fft_full_shape[1] - value.shape[1]
        if (zeros_to_add == 0):
            break
        zeros = np.zeros((rgb_fft_full_shape[0], zeros_to_add))
        rgb_fft[index] = np.c_[value, zeros]


    # Split R G and B into the dict 'rgb_fft'
    # Create a dict 'rgb_info', which is pre sorted, that will contain the ifft and compressed irfft data
    rgb_fft = {"Red": rgb_fft[0], "Green": rgb_fft[1], "Blue": rgb_fft[2]}
    rgb_info = {"Red": None, "Green": None, "Blue": None}  # Pre sorted
    rgb_array_fft = []
    threads = []

    # Compute
    for key, value in rgb_fft.items():
        process = threading.Thread(target=lambda q, arg1: q.update({key: decompress(arg1)}), args=(rgb_info, value))
        process.daemon = True
        process.start()
        threads.append(process)

    # Wait for all tasks to finish
    for process in threads:
        process.join()

    for value in rgb_info.values():
        rgb_array_fft.append(value.astype(np.uint8))

    rgb = np.stack(rgb_array_fft, axis=2)

    print("Image decompressed")
    return rgb

"""
Save image as jpg

:param: file name
:param: numpy 3D array
"""
def save_image(file_name, rgb):
    print("Saving image")
    file_name = "{}.jpg".format(file_name)
    imageio.imwrite(file_name, rgb)
    size = os.path.getsize(file_name)
    print("File saved as: {}.npz\nSize: {}MB".format(file_name, round(size / (1024 * 1024), 2)))

"""
Save image as jpg

:param: file name
:param: list of numpy 2D array
:param: list of full image shape
:param: compression percentage
"""
def save_fft(file_name, rgb_fft, rgb_fft_full_shape, compression):
    print("Saving image")
    file_name = "{}_comp_{}_fft".format(file_name, compression)
    file_obj = np.array([rgb_fft_full_shape, rgb_fft], dtype=object)
    np.savez_compressed(file_name, file_obj, allow_pickle=True)
    size = os.path.getsize(file_name + ".npz")
    print("File saved as: {}.npz\nSize: {}MB".format(file_name, round(size / (1024 * 1024), 2)))

"""
Program menu
"""
def menu():
    choice = input("[c]ompress, [d]ecompress, [a]ll (press h for help): ").lower()

    while True:
        if choice.startswith("c") or choice == "compress":
            file_name, rgb = read_raw_file()
            rgb_fft, rgb_fft_full_shape, compression = compress_fft(rgb)
            save_fft(file_name, rgb_fft, rgb_fft_full_shape, compression)
            break

        elif choice.startswith("d") or choice == "decompress":
            file_name, rgb_fft, rgb_fft_full_shape = read_fft_file()
            image = decompress_fft(rgb_fft, rgb_fft_full_shape)
            save_image(file_name, image)
            break

        elif choice.startswith("a") or choice == "all":
            file_name, rgb = read_raw_file()
            rgb_fft, rgb_fft_full_shape, compression = compress_fft(rgb)
            image = decompress_fft(rgb_fft, rgb_fft_full_shape)

            file_name = "{}_comp_{}_fft".format(file_name, compression)
            save_image(file_name, image)
            break

        elif choice.startswith("h") or choice == "help":
            print("Type 'c' for compression of a RAW image.\nType 'd' for decompression of a FFT image.\nType 'a' to compress and decompress an image.")
            break

        else:
            if choice.lower() == "q":
                raise SystemExit
            choice = input("Incorrect input parameter, try again. (press q to quit) ")

if __name__ == '__main__':
    menu()
