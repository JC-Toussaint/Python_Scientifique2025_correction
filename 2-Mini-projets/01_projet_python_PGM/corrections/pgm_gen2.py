# -*- coding: utf-8 -*-
"""
Created on Thu Dec 16 13:37:12 2021

@author: toussaij
"""

# Generation d'un fichier image au format PGM

#import numpy as np
import math
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
from PIL import Image
from time import process_time

MAXDEG =255
MAXTAIL=256

def centering(i, L):
    return (2.0*i-L)/L

def fun(x, y):
    """ f(x,y)=0.5*(sin(x)*sin(y)+1) in [0, 1]  """
    return 0.5*(np.sin(x)*np.sin(y)+1.0)
 
def createImg(fun, NROWS, NCOLS, NLEVELS=255):   
    img = np.zeros(shape=(NROWS, NCOLS), dtype='uint8')
    for i in range(NROWS):
        x = centering(i, NROWS)*np.pi
        for j in range(NCOLS):
            y = centering(j, NCOLS)*np.pi
            img[i, j]=math.floor(fun(x,y)*NLEVELS)
    return img
    
def createImgVec(fun, NROWS, NCOLS, NLEVELS=255):    
    x = np.arange(0, NROWS)
    x = centering(x, NROWS)*np.pi
    y = np.arange(0, NCOLS)
    y = centering(y, NCOLS)*np.pi
    X, Y = np.meshgrid(x, y)
    A=np.floor(fun(X, Y)*NLEVELS).astype(np.uint8)
    return A

def threshold(A, thres):
    A[A>thres]=thres
    return A

def savePGMarray(PGMarr, filename):
    nrows, ncols = PGMarr.shape
    nlevs = PGMarr.max()
    
    with open(filename, 'w') as f:
        f.write('P2\n')
        f.write(str(ncols)+' '+str(nrows)+'\n')
        f.write(str(nlevs)+'\n')
        for row in PGMarr:
            for e in row:
                chaine = "{var:4d}".format(var=e)            
                f.write(chaine+' ')
            f.write('\n')
          
def genPGMfile(fun, filename):
    with open(filename, 'w') as f:
        f.write('P2\n')
        f.write(str(MAXTAIL)+' '+str(MAXTAIL)+'\n')
        f.write(str(MAXDEG)+'\n')
     
    with open(filename, 'ab') as f: 
        for ix in range(MAXTAIL):
            for iy in range(MAXTAIL):
                x = centering(ix, MAXTAIL)*math.pi
                y = centering(iy, MAXTAIL)*math.pi
                z=math.floor(fun(x,y)*MAXDEG)
                f.write(z.to_bytes(1, byteorder='big'))
    
def readImg(filename):
    with open(filename, 'rb') as f:
        for line in f:
            # Ignores commented lines
            if line[0] != '#':
                break
            
    # Makes sure it is ASCII format (P2)
    # leading and trailing whitespace removed
        assert line.strip() == b'P2'   # bytes

    # Converts data to a list of integers
        data = []
        line = f.readline()
        lst = line.split()
        ncols = int(lst[0])
        data.append(ncols)  
        nrows = int(lst[1])
        data.append(nrows)  
   
        line = f.readline()
        lst = line.split()
        nlevs = int(lst[0])
        data.append(nlevs)  
        
        for n in range(nrows*ncols):
            val = int.from_bytes(f.read(1), "big")
            data.append(val)
                         
    return (np.array(data[3:]),(data[1],data[0]),data[2])
   
genPGMfile(fun, 'tata.pgm')
# im = Image.open("toto.pgm")
# print(im.format, im.size, im.mode)
# im.show()

# with open('toto.pgm', 'r') as pgmf:
#     im = plt.imread(pgmf, format='pgm')
    


data = readImg('toto.pgm')
print(data[0])
print(data[1])
print(data[2])

plt.close()
plt.figure()
plt.imshow(np.reshape(data[0],data[1]), cmap=cm.jet) # Usage example
plt.colorbar()
plt.show()

# Start the stopwatch / counter 
t1_start = process_time() 
   
Z=createImgVec(fun, MAXTAIL, MAXTAIL)
 
# Stop the stopwatch / counter
t1_stop = process_time()
print("Elapsed time:", t1_stop-t1_start) 
   
plt.figure()
plt.imshow(Z, cmap=cm.jet)
plt.colorbar()
plt.show()

savePGMarray(Z, 'titi.pgm')
   
Z=threshold(Z, 192)
plt.figure()
plt.imshow(Z, cmap=cm.jet)
plt.colorbar()
plt.show()
 
#Z = (Z * 255).astype(np.uint8)
im = Image.fromarray(Z)
im.save('titi.jpeg')
        