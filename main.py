import numpy as np
import cv2
from PyQt6.QtWidgets import QApplication, QWidget

cap = cv2.VideoCapture(0)
face_cascade_db = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
eye_cascade_db = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

if not cap.isOpened():
    print('Нет камеры')

while True:
    ret, frame = cap.read()
    
    if not ret:
        print("404")
        exit() 

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    #лицо
    face = face_cascade_db.detectMultiScale(gray, 1.1, 19)
    for (x,y,w,h) in face:
        cv2.rectangle(frame, (x,y), (x+w,y+h), (0,255,0), 2)

        #глаза
        gray_fase = gray[y:y+h,x:x+w]
        eyes = eye_cascade_db.detectMultiScale(gray_fase, 1.1, 19)
        for (ex, ey, ew, eh) in eyes:
            cv2.rectangle(frame, (x+ex, y+ey),(x+ex + ew, y+ey + eh), (255,0,0), 2)


        if len(eyes) == 0:
            print('не видно')

    cv2.imshow('frame', frame)

    if cv2.waitKey(1) & 0xff == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
