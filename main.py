import numpy as np
import cv2
from PyQt6.QtWidgets import QApplication, QWidget
import time

def time_input(time_user):
    pass





def base_program():
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

            if len(face) == 0:
                print('не видно')

            #глаза
            gray_fase = gray[y:y+h,x:x+w]
            eyes = eye_cascade_db.detectMultiScale(gray_fase, 1.1, 19)
            for (ex, ey, ew, eh) in eyes:
                cv2.rectangle(frame, (x+ex, y+ey),(x+ex + ew, y+ey + eh), (255,0,0), 2)

                if len(eyes) == 0:
                    print("глаз не видно")


        cv2.imshow('frame', frame)

        if cv2.waitKey(1) & 0xff == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    return # конец

def main():
    base_program()


if __name__ == '__main__':
    main()

