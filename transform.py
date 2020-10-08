import matplotlib.pyplot as plt
import numpy as np
import rawpy as rp
import scipy
from scipy.fftpack import fft

from PIL import Image

raw = rp.imread("skulls.NEF") #skulls.NEF = file_name
bayer = raw.raw_image
im = raw.postprocess() #rgb = ..

rgb = [im[:,:,0], im[:,:,1], im[:,:,2]]
arrays = []
compression = 0


for color in rgb:
    ahat = np.fft.rfft2(color)
    thresh = 0.000004 * np.amax(np.absolute(ahat))
    ind = np.absolute(ahat)>thresh
    ahatFilt = ahat*ind
    count = ahat.size - ind.sum()
    percent = 100-count/(ahat.size)*100
    Afilt = np.fft.irfft2(ahatFilt).astype(np.uint8)
    arrays.append(Afilt)
    compression = compression + percent


total_compression = str(round(compression/3, 2))
title = "Compression to " + total_compression + "% of original."
rgb_compressed = np.stack(arrays, axis=2)
plt.title(title)
plt.imshow(rgb_compressed)
plt.show()
