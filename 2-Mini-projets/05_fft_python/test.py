%matplotlib inline

import numpy as np
import matplotlib.pyplot as plt
import scipy.ndimage.filters as filter
import scipy.fftpack as fftpack

def kern(t, T):
    return np.sin(2*np.pi*t/T)

T=1
t=np.linspace(0, T, 100, endpoint=False)
G=kern(t, T)

fig=plt.figure()
ax = fig.add_subplot(111)
fig.subplots_adjust(top=0.85)
ax.set_title('kernel')

ax.set_xlabel('t')
ax.set_ylabel('G(t)')

plt.plot(t, G)
plt.grid(True)
plt.draw()
    
fftG = fftpack.fft(G)

fig=plt.figure()
ax = fig.add_subplot(121)
fig.subplots_adjust(top=0.85)
ax.set_title('Real Part')
plt.plot(fftG.real, 'r.')
plt.grid(True)

ax=plt.subplot(122)
fig.subplots_adjust(top=0.85)
ax.set_title('Imag Part')
plt.plot(fftG.imag, 'b.')

plt.grid(True)
plt.draw()
