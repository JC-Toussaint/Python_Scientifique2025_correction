# -*- coding: utf-8 -*-
"""
Created on Fri May  6 19:01:46 2022

@author: toussaij
"""

import numpy as np
import cv2

from matplotlib import pyplot as plt

img = cv2.imread('pieces.jpg')

gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

ret, thresh = cv2.threshold(gray,0,255,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
 
# affichage dans une fenetre graphique, 1er param : nom de la fenetre, 2e param : image array
cv2.imshow("seg", thresh)
 
# attente en ms sinon appui d'une touche dans la fenetre graphique
cv2.waitKey(0)
 

# noise removal
kernel = np.ones((3,3),np.uint8)
opening = cv2.morphologyEx(thresh,cv2.MORPH_OPEN,kernel, iterations = 2)
cv2.imshow("seg", opening)

# sure background area
sure_bg = cv2.dilate(opening,kernel,iterations=3)
# Finding sure foreground area
dist_transform = cv2.distanceTransform(opening,cv2.DIST_L2,5)
cv2.imshow("dist_transform", dist_transform)
# attente en ms sinon appui d'une touche dans la fenetre graphique
cv2.waitKey(0)

ret, sure_fg = cv2.threshold(dist_transform,0.7*dist_transform.max(),255,0)

cv2.imshow("seg", sure_fg)

# attente en ms sinon appui d'une touche dans la fenetre graphique
cv2.waitKey(0)

# Finding unknown region
sure_fg = np.uint8(sure_fg)
unknown = cv2.subtract(sure_bg,sure_fg)

cv2.imshow("seg", unknown)

# attente en ms sinon appui d'une touche dans la fenetre graphique
cv2.waitKey(0)

# OBLIGATOIRE appel des destructeurs et desallocation memoire
cv2.destroyAllWindows()