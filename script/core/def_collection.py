import sys
import cv2
import numpy as np
import json
import os
import time
import tempfile
import shutil

FACE_CASCADE = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml') # type: ignore
EYE_CASCADE = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml') # type: ignore
EYE_GLASSES_CASCADE = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye_tree_eyeglasses.xml') # type: ignore

def load_config(config_path='config.json'):
    try:
        with open(config_path, "r", encoding='utf-8') as f:
            data = json.load(f)
            return data["selected_file"], data["gaze_enabled"], data["glasses_enabled"], data["work_time_seconds"]
    except Exception as e:
        print(f"Ошибка загрузки конфигурации: {e}")
        sys.exit()

def get_safe_path(orig_path):
    if not orig_path or not os.path.exists(orig_path):
        return None
    
    suffix = os.path.splitext(orig_path)[1]
    fd, temp_path = tempfile.mkstemp(suffix=suffix)
    os.close(fd)

    shutil.copy2(orig_path, temp_path)
    return temp_path

def error_window(should_show, is_active, bg_image):
    if should_show and not is_active:
        cv2.imshow("Error", bg_image)
        cv2.moveWindow("Error",  500, 300)
        return True
    elif not should_show and is_active:
        cv2.destroyWindow("Error")
        return False
    return is_active

def detect_main(file: str, gaze: bool, glasses_enabled: bool, work_time: int):
    temp_name = get_safe_path(file)

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FPS, 24)

    start_time = time.time()
    total_pause_duration = 0
    face_lost_time = None
    eyes_lost_time = None
    cooldown_until = 0
    error_window_active = False
    is_paused = False
    pause_start = 0

    error_bg = np.zeros((300, 400, 3), dtype=np.uint8)

    try:
        while cap.isOpened():
            curr_t = time.time()
            key = cv2.waitKey(1) & 0xFF

            if key == ord('q'):break
            if key == ord('p'):
                is_paused = not is_paused
                if is_paused:
                    pause_start = curr_t
                    error_window_active = error_window(False, error_window_active, error_bg)
                else:
                    total_pause_duration += (curr_t - pause_start)

            ret, frame = cap.read()
            if not ret: break

            if is_paused:
                cv2.imshow("Main Stream", frame)
                continue
                
            if (curr_t - start_time - total_pause_duration) >= work_time:
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = FACE_CASCADE.detectMultiScale(gray, 1.3, 5)

            face_detected = len(faces) > 0
            eyes_detected =  False

            if face_detected:
                (x, y, w, h) = faces[0]
                cv2.rectangle(frame, (x,y), (x+w, y+h), (255, 0, 0), 2)
                roi_gray = gray[y:y+h, x:x+w]

                cascade = EYE_GLASSES_CASCADE if glasses_enabled else EYE_CASCADE
                eyes = cascade.detectMultiScale(roi_gray, 1.1, 10)
                eyes_detected = len(eyes) >= 2

                for (ex, ey, ew, eh) in eyes:
                    cv2.rectangle(frame, (x+ex, y+ey), (x+ex+ew, y+ey+eh), (0, 255, 0), 2)
            
            should_error = False

            in_cooldown = curr_t < cooldown_until

            if not face_detected and not in_cooldown:
                if face_lost_time is None: face_lost_time = curr_t
                if curr_t - face_lost_time >= 1.0: should_error = True
            else:
                face_lost_time = None
            
            if face_detected and not eyes_detected and not in_cooldown:
                if eyes_lost_time is None: eyes_lost_time = curr_t
                if curr_t - eyes_lost_time >= 1.3: should_error = True
            else:
                eyes_lost_time = None
            
            was_active = error_window_active
            error_window_active = error_window(should_error, error_window_active, error_bg)

            if was_active and not error_window_active:
                cooldown_until = curr_t + 3
            
            cv2.imshow("Main Stream", frame)
        
    finally:
        cap.release()
        cv2.destroyAllWindows()
        if temp_name and os.path.exists(temp_name):
            try: os.remove(temp_name)
            except: print("Error del file"); pass


def main():
    config = load_config()
    detect_main(*config)

if __name__ == "__main__":
    main()