from PIL import Image
import imagehash
from os import listdir
import sys
import time
import cv2
import numpy as np
import time

# пробуем гистограмму


def getHist(img):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    # extract a 3D RGB color histogram from the image,
    # using 8 bins per channel, normalize, and update
    # the index
    hist = cv2.calcHist([img], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
    return cv2.normalize(hist, hist).flatten()


hist1 = getHist(cv2.imread("exact_pics/smiths_04.jpg"))
# hist2 = getHist(cv2.imread("exact_pics/smiths_04.jpg"))
# hist2 = getHist(cv2.imread("exact_pics/smiths_05.jpg"))
hist2 = getHist(cv2.imread("exact_pics/legomovie_01.jpg"))

method = cv2.HISTCMP_BHATTACHARYYA

d = cv2.compareHist(hist1, hist2, cv2.HISTCMP_BHATTACHARYYA)

print('result')
print(d)
