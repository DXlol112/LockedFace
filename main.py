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

    face = face_cascade_db.detectMultiScale(gray, 1.1, 19)
    for (x,y,w,h) in face:
        cv2.rectangle(frame, (x,y), (x+w,y+h), (0,255,0), 2)

    eye = eye_cascade_db.detectMultiScale(gray, 1.1, 19)
    for (x,y,w,h) in eye:
        cv2.rectangle(frame, (x,y), (x+w,y+h), (255,0,0), 2)
        
    cv2.imshow('frame', frame)
    
    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
<<<<<<< HEAD
cv2.destroyAllWindows()
=======
cv2.destroyAllWindows()
>>>>>>> 3d426532d0c5b602ad7d9cde0c1570e723439b85
