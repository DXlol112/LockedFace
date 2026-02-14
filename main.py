import numpy as np
import cv2
import sys
eyeCascade = cv2.CascadeClassifier('haarcascade_eye.xml')
cam = cv2.VideoCapture(0)

while True:
    ret, frame = cam.read()
    roi = frame[269:795, 200:600]
    gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    
    eyes = eyeCascade.detectMultiScale(gray_roi, 1.3, 5)
    for (ex, ey, ew, eh) in eyes:
        eye_roi = gray_roi[ey:ey+eh, ex:ex+ew]
        _, threshold = cv2.threshold(eye_roi, 70, 255, cv2.THRESH_BINARY)
    
    # contur = cv2.findContours(threshold, cv2)

    cv2.imshow('frame', threshold)
    key = cv2.waitKey(30)
    if key == 27:
        break


cv2.destroyAllWindows()
