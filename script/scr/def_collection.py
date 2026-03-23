import numpy as np
import pathlib as pl
import cv2
import PyQt6.QtWidgets as qtw
import time
import shutil
import sys

def select_img_or_mp4_save()-> str|None: # выбор фала для ошибки пользоватьеля #сделать ситему сохронения при выходе из приложения
    file_path, _ = qtw.QFileDialog.getOpenFileName(None, "Выберете файл", "", "Image/Video (*.jpg *.png *.mp4 *.webp)")
    if not file_path:
        return None
    
    src_path = pl.Path(file_path)

    project_dir = pl.Path(__file__).resolve().parent.parent.parent
    
    media_dir = project_dir / "media"
    media_dir.mkdir(exist_ok=True)

    dest_path = media_dir / src_path.name

    if dest_path.exists():
        return str(dest_path)

    try:
        shutil.copy(file_path, dest_path)
        return str(dest_path)
    
    except Exception as e:
        print(f"Ошибка при копировании файла: {e}")
        return None
    

def select_media_user():
    user_dir = pl.Path(__file__).resolve().parent.parent.parent
    media_dir = user_dir / "media"

    files = sorted([f for f in media_dir.iterdir() if f.is_file()])

    if not files:
        print("Нет файлов в папке media")
        return None
    
    print("Выберите файл:")
    for i, f in enumerate(files, 1):
        print(f"{i}. {f.name}")

    try:
        input_index = int(input("Введите номер файла: "))
        return str(files[input_index-1])
    
    except (ValueError, IndexError):
        print("Ошибка выбора")
        return select_media_user()

# def update_time(h, m, s, dh=0, dm=0, ds=0): #ввод времини. #обеденить в одном UI
#     h = (h + dh) % 24
#     m = (m + dm) % 60
#     s = (s + ds) % 60 
#     return h, m, s


def base_program(time_inp: int, img_or_mp4: str, gaze_off_or_on: int) -> None:  # Основа програмы
    cap = cv2.VideoCapture(0)

    violation_img = cv2.imread(img_or_mp4)
    if violation_img is None:
        print("Ошибка загрузки изображения нарушения")
        return
    
    start_time = time.time()
    
    face_cascade_db = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml') # type: ignore
    eye_cascade_db = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml') # type: ignore

    eyes_closed_time = None
    face_not_detected_time = None
    gaze_time = None

    
    
    if not cap.isOpened():
        print('Нет камеры')
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            print("404")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade_db.detectMultiScale(gray, 1.1, 10, minSize=(100, 100))

        if len(faces) > 0:
            (x, y, w, h) = faces[0]
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            face_not_detected_time = None
            try:
                cv2.destroyWindow("Violation_face")
            except:
                pass

            gray_roi = gray[y:y + h, x:x + w]
            color_roi = frame[y:y + h, x:x + w]

            eyes = eye_cascade_db.detectMultiScale(gray_roi, 1.1, 20, minSize=(30, 30))            
            
            if len(eyes) > 0:    
                for (ex, ey, ew, eh) in eyes[:2]:
                    cv2.rectangle(color_roi, (ex, ey), (ex + ew, ey + eh), (255, 0, 0), 2)
                
                    if gaze_off_or_on == 1:
                        
                        gaze = detect_gaze(color_roi[ey:ey + eh, ex:ex + ew])
                        cv2.rectangle(color_roi, (ex, ey), (ex + ew, ey + eh), (255, 0, 0), 2)

                        if gaze != "Center":

                            if gaze_time is None:
                                gaze_time = time.time()
                            
                            elif time.time() - gaze_time > 2:
                                cv2.imshow("Violation_eyes", violation_img)
                            
                        else:
                            gaze_time = None
                            try:
                                cv2.destroyWindow("Violation_eyes")
                            except:
                                pass


                eyes_closed_time = None
                try:
                    cv2.destroyWindow("Violation_eyes")
                except:
                    pass

            else:

                if eyes_closed_time is None:
                    eyes_closed_time = time.time()
                
                elif time.time() - eyes_closed_time > 1.5:
                    cv2.imshow("Violation_eyes", violation_img)
        else:

            if face_not_detected_time is None:
                face_not_detected_time = time.time()

            elif time.time() - face_not_detected_time > 0.5:
                cv2.imshow("Violation_face", violation_img)

            
                
        cv2.imshow("Frame", frame)
        cv2.resizeWindow("Frame", 800, 600)
        close_time = time.time() - start_time
        if cv2.waitKey(1) & 0xff == ord('q') or close_time > time_inp:
            break

    cap.release()
    cv2.destroyAllWindows()
    return # конец


def detect_gaze(gray_roi):# доп функция для определения направления взгляда. #дополнить и улучшить
    gray_roi = cv2.cvtColor(gray_roi, cv2.COLOR_BGR2GRAY)
    gray_roi = cv2.GaussianBlur(gray_roi, (7, 7), 0)

    _, thresh = cv2.threshold(gray_roi, 50, 255, cv2.THRESH_BINARY_INV)

    h, w = thresh.shape

    left_white = cv2.countNonZero(thresh[:, :int(w / 2)])
    right_white = cv2.countNonZero(thresh[:, int(w/2):w])

    if left_white > right_white:
        return "Right"
    elif right_white > left_white:
        return "Left"
    else:
        return "Center"
        

def main():
    app = qtw.QApplication(sys.argv)
    path = select_img_or_mp4_save()
    media_user = select_media_user()

    time_inp = 100000000  ###time_input()
    if time_inp > 0:
        try:
            gaze_off_or_on = int(input("Включить определение направления взгляда? (1 - да, 0 - нет): "))
        except ValueError:
            print("Некорректный ввод. Выключение определения направления взгляда по умолчанию.")
            gaze_off_or_on = 0

        base_program(time_inp, media_user, gaze_off_or_on)


if __name__ == '__main__':
    main()
