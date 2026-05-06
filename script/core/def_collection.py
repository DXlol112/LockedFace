import cv2
import numpy as np
import json
import os
import sys
import time 
import tempfile
import shutil
from ffpyplayer.player import MediaPlayer

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

try:
    import mediapipe.solutions.face_mesh as mp_face_mesh # type: ignore
except ImportError:
    try:
        from mediapipe.python.solutions import face_mesh as mp_face_mesh
    except ImportError:
        sys.exit("Ошибка: Не удалось найти модуль FaceMesh в установленном mediapipe.")


face_mesh = mp_face_mesh.FaceMesh(
    max_num_faces=1, 
    refine_landmarks=True, 
    min_detection_confidence=0.5, 
    min_tracking_confidence=0.5
)

def load_config(config='config.json'):
    try:
        with open(config, "r", encoding='utf-8') as f:
            data = json.load(f)
            return data["selected_file"], data["gaze_enabled"], data["glasses_enabled"], data["work_time_seconds"]
    except Exception as e:
        sys.exit(f"Ошибка загрузки конфигурации: {e}")
    
def get_safe_path(orig_path):
    if not orig_path or not os.path.exists(orig_path): return None
    _, ext = os.path.splitext(orig_path)
    fd, temp_path = tempfile.mkstemp(suffix=ext)
    os.close(fd)
    shutil.copy2(orig_path, temp_path)
    return temp_path

def is_eye_open(landmarks, eye_indices, glass_enabled):
    p1 = landmarks[eye_indices[0]]
    p2 = landmarks[eye_indices[1]]
    dist = np.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2) 
    if glass_enabled:
        return dist > 0.005
    else:
        return dist > 0.018


def detect_main(file: str, gaze: bool, glasses_enabled: bool, work_time: int) -> None: # glasses_enabled -> stub
    temp_name = get_safe_path(file)
    cap = cv2.VideoCapture(0)
    
    error_player = None
    error_cap = None
    
    eyes_lost_time = 0.0
    cooldown_until = 0.0
    error_window_active = False
    is_paused = False
    pause_start = 0.0
    start_time = time.time()
    total_pause_duration = 0

    LEFT_EYE = [386, 374]
    RIGHT_EYE = [159, 145]

    try:
        while cap.isOpened():
            curr_t = time.time()
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord("q"): break
            if key == ord("p"):
                is_paused = not is_paused
                if is_paused:
                    pause_start = curr_t
                    if error_player: error_player.set_pause(True)
                else:
                    total_pause_duration += (curr_t - pause_start)
                    if error_player: error_player.set_pause(False)
                continue
            
            ret, frame = cap.read()
            if not ret: break
            
            if is_paused:
                cv2.putText(frame, "PAUSE", (50, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 2)
                cv2.imshow("Main stream", frame)
                continue

            if (curr_t - start_time - total_pause_duration) >= work_time:
                print("Конец рабочего времени")
                break
        
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = face_mesh.process(rgb_frame)

            face_detected = False
            eyes_detected = False

            if results.multi_face_landmarks: # type: ignore
                face_detected = True
                landmarks = results.multi_face_landmarks[0].landmark # type: ignore

                for idx in LEFT_EYE + RIGHT_EYE:
                    pt = landmarks[idx]
                    cv2.circle(frame, (int(pt.x * frame.shape[1]), int(pt.y * frame.shape[0])), 2, (0, 255, 0), -1)

                if gaze:
                    left_open, right_open = is_eye_open(landmarks, LEFT_EYE, glasses_enabled), is_eye_open(landmarks, RIGHT_EYE, glasses_enabled)
                    eyes_detected = left_open or right_open
                else:
                    eyes_detected = True
            

            should_error = False
            in_cooldown = curr_t < cooldown_until

            if (not face_detected or not eyes_detected) and not in_cooldown:
                if eyes_lost_time == 0: eyes_lost_time = curr_t
                if curr_t - eyes_lost_time >= 1.3:
                    should_error = True
            else:
                eyes_lost_time = 0

            if should_error:
                if not error_window_active:
                    if temp_name:
                        ext = os.path.splitext(temp_name)[1].lower()
                        if ext in ['.jpg', '.jpeg', '.png']:
                            error_cap = None 
                        else:
                            error_player = MediaPlayer(temp_name)
                            error_cap = cv2.VideoCapture(temp_name)
                        error_window_active = True
                    else:
                        print("Ошибка: Временный файл не создан")
                        continue

                if error_cap:
                    res, e_frame = error_cap.read()
                    audio_frame, val = error_player.get_frame() if error_player else (None, 0)
                    
                    if not res:
                        error_cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                        res, e_frame = error_cap.read()

                    if val != 'eof' and val > 0:
                        current_video_time = error_cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0
                        wait_time = val - current_video_time
                        if wait_time > 0:
                            time.sleep(wait_time)

                    cv2.imshow("Error", e_frame)
                else:
                    img = cv2.imread(temp_name) # pyright: ignore[reportArgumentType, reportCallIssue]
                    if img is not None: cv2.imshow("Error", img)
                    
            elif error_window_active:
                if error_player: error_player.close_player(); error_player = None
                if error_cap: error_cap.release(); error_cap = None
                try: cv2.destroyWindow("Error")
                except: pass
                error_window_active = False
                cooldown_until = curr_t + 3

            cv2.imshow("Main stream", frame)

    finally:
        if error_player: error_player.close_player()
        if error_cap: error_cap.release()
        cap.release()
        cv2.destroyAllWindows()
        if temp_name and os.path.exists(temp_name):
            try: os.remove(temp_name)
            except: pass

if __name__ == "__main__":
    parameter = load_config()
    detect_main(*parameter)
