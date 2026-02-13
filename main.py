import numpy as np
import cv2
import sys
eyeCascade = cv2.CascadeClassifier(cascPath)
cam = cv2.VideoCapture(0)

while True:
    ret, frame = cam.read()
    roi = frame[269:795, 200:600]
    gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    
    eyes = c

    _, threshold = cv2.threshold(gray_roi, 5, 255, cv2.THRESH_BINARY_INV)

    cv2.imshow('frame', threshold)
    key = cv2.waitKey(30)
    if key == 27:
        break


cv2.destroyAllWindows()
