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

#print(rgb[0].size)
for color in rgb:
    ahat = np.fft.rfft2(color)
    #print(ahat.size)
    #F = np.log(np.absolute(np.fft.fftshift(ahat))+1)
    """plt.gray()
    plt.imshow(F)
    plt.show()"""
    thresh = 0.00001 * np.amax(np.absolute(ahat))
    ind = np.absolute(ahat)>thresh
    #ind = ind.transpose()
    ahatFilt = ahat*ind
    count = ahat.size - ind.sum()
    percent = 100-count/(ahat.size)*100
    Afilt = np.fft.irfft2(ahatFilt).astype(np.uint8)
    arrays.append(Afilt)
    print(percent)

rgb_compressed = np.stack(arrays, axis=2)
plt.imshow(rgb_compressed)
plt.show()

#stores all rgb values from rgb separately in an array of lists. index corresponds to row index. r[0] is r all 'r' values from top row
"""
r = deepcopy(rgb)
g = deepcopy(rgb)
b = deepcopy(rgb)

r[:,:,1] = 0
r[:,:,2] = 0

g[:,:,0] = 0
g[:,:,2] = 0

b[:,:,0] = 0
b[:,:,1] = 0

fig, ax = plt.subplots(nrows=2, ncols=2)

ax[0,0].imshow(rgb)
ax[0,1].imshow(r)
ax[1,0].imshow(g)
ax[1,1].imshow(b)

plt.show()"""


"""
r = rgb[:,:,0]
g = rgb[:,:,1]
b = rgb[:,:,2]

row = 2352
N = len(r[row])   # sample count
T = 1/1000.0 #[Hz] # sample frequency

x = np.linspace(0.0, N/T, N)
y = np.sin(50.0 * 2.0*np.pi*x) + 0.5*np.sin(80.0 * 2.0*np.pi*x)
rf = scipy.fftpack.fft(r[row])
xf = np.linspace(0.0, 1.0/(2.0*T), N//2)

rf_real = 2.0/N * np.abs(rf[:N//2])

fig, ax = plt.subplots()
ax.plot(xf, rf_real)
plt.show()

rf_real = [x for x in rf_real if x > 100]
print(rf_real)
"""




