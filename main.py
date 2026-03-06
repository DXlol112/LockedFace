import numpy as np
import pathlib as pl
import cv2
import PyQt6.QtWidgets as qtw
import time
import sys
import os
import shutil

def select_img_or_mp4()-> str: # выбор фала для ошибки пользоватьеля #сделать ситему сохронения при выходе из приложения
    file_path, _ = qtw.QFileDialog.getOpenFileName(None, "Выберете файл", "", "Image/Video (*.jpg *.png *.mp4 *.avi)")
    return file_path

def save_file_path_on_disk(file_path:str)-> str:
    if not file_path:
        return ""

    project_dir = pl.Path(__file__).parent

    save_dir = project_dir / "project_media"
    save_dir.mkdir(exist_ok=True)

    file_name = pl.Path(file_path).name
    distutils = save_dir / file_name

    try:
        shutil.copy(file_path, distutils)
        return str(distutils)
    except Exception as e:
        print(e)
        return ""

def select_media_user():
    user_dir = pl.Path(__file__).resolve().parent
    media_dir = user_dir / "project_media"

    files = sorted([f for f in media_dir.iterdir() if f.is_file()])

    print("Выберите файл")
    for i, f in enumerate(files, 1):
        print(f"{i}. {f.name}")

    try:
        input_user = int(input("Ваш выбор: "))
        return str(files[input_user-1])
    except (ValueError, IndexError):
        print("Ошибка выбора")
        return select_media_user()

def time_input()-> int: #ввод времини. #обеденить в одном UI
    pass


def base_program(time_inp: int, img_or_mp4: str) -> None:  # Основа програмы
    cap = cv2.VideoCapture(0)

    violation_img = cv2.imread(img_or_mp4)

    face_cascade_db = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    eye_cascade_db = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

    if not cap.isOpened():
        print('Нет камеры')
        return

    start_time = time.time()

    while True:
        ret, frame = cap.read()
        if not ret:
            print("404")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = face_cascade_db.detectMultiScale(gray, 1.1, 19, minSize=(100, 100))

        if len(faces) > 0:
            (x, y, w, h) = faces[0]
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            gray_roi = gray[y:y + h, x:x + w]
            eyes = eye_cascade_db.detectMultiScale(gray_roi, 1.1, 19, minSize=(40, 40))

            if len(eyes) < 2 and violation_img is not None:
                cv2.imshow("ALARM", violation_img)
            else:
                try:
                    if cv2.getWindowProperty("ALARM", cv2.WND_PROP_VISIBLE) >= 0:
                        cv2.destroyWindow("ALARM")
                except cv2.error:
                    pass

        cv2.imshow("Frame", frame)

        close_time = time.time() - start_time
        if cv2.waitKey(1) & 0xff == ord('q') or close_time > time_inp:
            break

    cap.release()
    cv2.destroyAllWindows()
    return # конец

def main():
    app = qtw.QApplication(sys.argv)
    file_path = select_img_or_mp4()

    if file_path:
        local_path = save_file_path_on_disk(file_path) #

    media_user = select_media_user()

    time_inp = 100000000  ###time_input()
    if time_inp > 0:
        base_program(time_inp, media_user)


if __name__ == '__main__':
    main()
