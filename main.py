import numpy as np
import pathlib as pl
import cv2
from PyQt6.QtWidgets import QApplication, QWidget
import time

def time_input()-> int: #ввод времини
    try:
        time_inp = int(input("Введите время работы: "))
        return time_inp
    except ValueError:
        print("Время ведено неправильно: ")
        return 0

def select_img_or_mp4()-> str:
    img_or_mp4 = []




def base_program(time_inp:int,img_or_mp4:str)->None:
    cap = cv2.VideoCapture(0)
    face_cascade_db = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    eye_cascade_db = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

    if not cap.isOpened():
        print('Нет камеры')

    start_time = time.time()


    while True:
        ret, frame = cap.read()

        if not ret:
            print("404")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        #лицо
        face = face_cascade_db.detectMultiScale(gray, 1.1, 19,minSize=(100, 100))
        if len(face) > 0:
            (x, y, w, h) = face[0]
            cv2.rectangle(frame, (x,y), (x+w,y+h), (0,255,0), 2)

            #глаза
            gray_fase = gray[y:y+h,x:x+w]
            eyes = eye_cascade_db.detectMultiScale(gray_fase, 1.1, 19, minSize=(40, 40))
            for (ex, ey, ew, eh) in eyes:
                cv2.rectangle(frame, (x+ex, y+ey),(x+ex + ew, y+ey + eh), (255,0,0), 2)

                if len(eyes) < 2:
                    cv2.imshow('violation')


        cv2.imshow('frame', frame)

        close_time = time.time() - start_time

        if cv2.waitKey(1) & 0xff == ord('q') or time_inp > close_time:
            break

    cap.release()
    cv2.destroyAllWindows()
    return # конец

def main():
    time_inp = time_input()
    if time_inp > 0:
        base_program(time_inp)

if __name__ == '__main__':
    main()

