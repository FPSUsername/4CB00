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
def read_raw_file():
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
Reads a FFT image file
Returns the 3D array
"""
def read_fft_file():
    file_name = input("File name: ")
    if not os.path.isfile(file_name):
        print ("File does not exist")
        raise SystemExit

    rgb_fft = np.load(file_name)

    file_name = os.path.splitext(file_name)[0]
    return file_name, rgb_fft

"""
Use Matplotlib to plot the frequencies of each color
Explects a dict where each value consists of a list,
where the second key, [1], is the array of the frequencies
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
        b = rgb_comp[key][1]
        axes.append( fig.add_subplot(rows, cols, index + 1) )
        subplot_title=(key + " frequencies")
        axes[-1].set_title(subplot_title)
        plt.imshow(b)

    fig.tight_layout()
    plt.show()

"""
Compress a 2D array using FFT
Accepts a 2D array and a compression number [0, 100]
"""
def compress(color, compression):
    ahat = np.fft.rfft2(color)
    # Compress by throwing away low frequencies!
    F = np.log(np.absolute(np.fft.fftshift(ahat)) + 1)  # Frequencies in human readable form

    val = 0.00000004 * compression  # From 0 to 4e-6
    thresh = val * np.amax(np.absolute(ahat))
    ind = np.absolute(ahat)>thresh  # Matrix filled with 1 and 0
    ahatFilt = np.multiply(ahat, ind)  # Element wise multiplication

    count = ahat.size - np.sum(ind)  # Total number of nonzero Fourier coëfficients
    percent = 100 - count / (ahat.size) * 100  # Percentage kept in terms of FFT
    # comp_percent = compression + percent

    # Return the compressed image, the frequencies of each color and the compression percentage
    return [ahatFilt, F, percent]

"""
Decompress a FFT 2D array
Accepts a 2D array
"""
def decompress(color):
    Afilt = np.fft.irfft2(color)
    return Afilt

"""
Compress image using FFT
Accepts a 3D array
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
        rgb_array_fft.append(value[0])  # Complex

    rgb_fft = np.stack(rgb_array_fft, axis=2)

    # Show plots of each frequency
    answer = input("Check frequency graphs? [y/n] ")
    if answer.lower() == "y":
        plot_frequencies(rgb_info)

    print("Image compressed")
    return rgb_fft, compression

"""
Decompress FFT image
Accepts a dictionary with each color splitted.
"""
def decompress_fft(rgb_fft):
    print("Deompressing image")
    try:
        im = rgb_fft["arr_0"]
    except IndexError:
        im = rgb_fft
        print(im.shape)

    # Split R G and B into the dict 'rgb_fft'
    # Create a dict 'rgb_info', which is pre sorted, that will contain the ifft and compressed irfft data
    rgb_fft = {"Red": im[:,:,0], "Green": im[:,:,1], "Blue": im[:,:,2]}
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

def save_image(file_name, rgb):
    print("Saving image")
    file_name = "{}.png".format(file_name)
    imageio.imwrite(file_name, rgb)
    size = os.path.getsize(file_name + ".png")
    print("File saved as: {}.npz\nSize: {}MB".format(file_name, round(size / (1024 * 1024), 2)))

def save_fft(file_name, rgb_fft, compression):
    print("Saving image")
    file_name = "{}_comp_{}_fft".format(file_name, compression)
    np.savez_compressed(file_name, rgb_fft)
    size = os.path.getsize(file_name + ".npz")
    print("File saved as: {}.npz\nSize: {}MB".format(file_name, round(size / (1024 * 1024), 2)))

def menu():
    choice = input("[c]ompress, [d]ecompress, [a]ll (press h for help): ").lower()

    while True:
        if choice.startswith("c") or choice == "compress":
            file_name, bayer, rgb = read_raw_file()
            rgb_fft, compression = compress_fft(rgb)
            save_fft(file_name, rgb_fft, compression)
            break

        elif choice.startswith("d") or choice == "decompress":
            file_name, rgb_fft = read_fft_file()
            image = decompress_fft(rgb_fft)
            save_image(file_name, image)
            break

        elif choice.startswith("a") or choice == "all":
            file_name, bayer, rgb = read_raw_file()
            rgb_fft, compression = compress_fft(rgb)
            image = decompress_fft(rgb_fft)

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
