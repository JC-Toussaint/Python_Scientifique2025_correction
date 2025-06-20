import matplotlib.pyplot as plt
import numpy as np
import math
import cmath

def fft_rec(a, fft_a):
   n=len(a)
   #print(n)
   fft_a=np.zeros(n, dtype=complex)
   omega=cmath.exp(-2.*math.pi/n*1j); 
   #print(omega)

   if n==1:
      fft_a[0]=a[0]
   else:
      m=n//2
      b=np.zeros(m)
      c=np.zeros(m)
      fft_b=np.zeros(m, dtype=complex)
      fft_c=np.zeros(m, dtype=complex)
      alpha=1
#slicing syntax [<start>:<end>:step]
      b=a[0::2]
      c=a[1::2]
#equiv
#      for i in range(0, m):
#	  b[i]=a[2*i]
#	  c[i]=a[2*i+1]

      fft_b=fft_rec(b, fft_b)
      fft_c=fft_rec(c, fft_c)

      for i in range(0, m):
	  fft_a[  i]=fft_b[i] + alpha*fft_c[i]
	  fft_a[m+i]=fft_b[i] - alpha*fft_c[i]
	  alpha=alpha*omega
 
   return fft_a

def plot_signal(n, a, pos):
    fig=plt.figure()
    ax = fig.add_subplot(111)
    mngr = plt.get_current_fig_manager()
    mngr.window.setGeometry(0+pos[0],0+pos[1],pos[2], pos[3])
    geom = mngr.window.geometry()
    print(geom)

    fig.subplots_adjust(top=0.85)
    ax.set_title('signal')

    ax.set_xlabel('n')
    ax.set_ylabel('signal')

    plt.plot(n, a, 'r-')
    plt.grid(True)
    mngr = plt.get_current_fig_manager()
    #plt.show()
    plt.draw()  

def plot_fft(freq, fft, pos):
    re_fft =fft.real;
    im_fft =fft.imag;

    fig=plt.figure()
    ax = fig.add_subplot(111)
    mngr = plt.get_current_fig_manager()
    #mngr.window.move(600, 600)
    mngr.window.setGeometry(0+pos[0],0+pos[1],pos[2], pos[3])
    geom = mngr.window.geometry()

    fig.subplots_adjust(top=0.85)
    ax.set_title('fast fourier transform')

    ax.set_xlabel('frequency')
    ax.set_ylabel('amplitude')

    plt.plot(freq, re_fft, 'r+')
    plt.plot(freq, im_fft, 'b+')
    plt.grid(True)
    plt.draw()


N=512
n= np.linspace(0, N, N, endpoint=False)
freq=2.*math.pi/N
a=np.sin(2.*math.pi*freq*n)
fft_a= fft_rec(a, [])

plot_signal(n, a, [0, 0, 450, 450])

freq= np.linspace(0., 1., N, endpoint=False)
plot_fft(freq, fft_a, [450, 0, 450, 450])

#fft numpy routine 
fft  = np.fft.fft(a)

re_fft =fft.real;
im_fft =fft.imag;
plot_fft(freq, fft, [900, 0, 450, 450])

plt.show()



