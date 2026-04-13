import cv2
import time
import mediapipe as mp
import numpy as np
import json

mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils

def load_image_unicode(path):
    """Чтение изображения из пути с кириллицей"""
    try:
        with open(path, "rb") as f:
            chunk = f.read()
        chunk_arr = np.frombuffer(chunk, dtype=np.uint8)
        img = cv2.imdecode(chunk_arr, cv2.IMREAD_COLOR)
        if img is None:
            print(f"Не удалось декодировать изображение: {path}")
        return img
    except Exception as e:
        print(f"Ошибка загрузки файла: {e}")
        return None
    
def get_ear(eye_points):
    """Вычисление Eye Aspect Ratio (EAR)"""
    v1 = np.linalg.norm(np.array(eye_points[1]) - np.array(eye_points[5]))
    v2 = np.linalg.norm(np.array(eye_points[2]) - np.array(eye_points[4]))
    h = np.linalg.norm(np.array(eye_points[0]) - np.array(eye_points[3]))
    return (v1 + v2) / (2.0 * h) if h > 0 else 0

def run_monitor(config_path='config.json'):
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except Exception:
        print("Конфиг не найден! Использую стандартные настройки.")
        config = {"gaze_enabled": True, "glasses_enabled": False, "work_time_seconds": 60}
    
    img_path = config.get("selected_file", "")
    use_gaze = config.get("gaze_enabled", True)
    has_glasses = config.get("glasses_enabled", False)
    run_duration = config.get("work_time_seconds", 60)

    violation_img = load_image_unicode(img_path)
    
    face_mesh = mp_face_mesh.FaceMesh(
        max_num_faces=1,
        refine_landmarks=True, 
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )
    
    drawing_spec = mp_drawing.DrawingSpec(thickness=1, circle_radius=1, color=(0, 255, 0))

    cap = cv2.VideoCapture(0)
    start_time = time.time()
    
    eyes_closed_start = None
    face_lost_start = None
    gaze_lost_start = None
    violation_active = False

    EAR_THRESHOLD = 0.17 if has_glasses else 0.21

    print(f"Мониторинг запущен на {run_duration} секунд...")

    while cap.isOpened():
        ret, frame = cap.read()
        elapsed = time.time() - start_time
        
        if not ret or (elapsed > run_duration):
            print("Время работы завершено.")
            break
    
        h, w, _ = frame.shape
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(rgb)
        
        current_violation = None

        if results.multi_face_landmarks:
            face_lost_start = None
            landmarks = results.multi_face_landmarks[0]

            mp_drawing.draw_landmarks(
                image=frame,
                landmark_list=landmarks,
                connections=mp_face_mesh.FACEMESH_TESSELATION,
                landmark_drawing_spec=None,
                connection_drawing_spec=drawing_spec)

            l_idx = [33, 160, 158, 133, 153, 144]
            r_idx = [362, 385, 387, 263, 373, 380]

            left_pts = [(landmarks.landmark[i].x * w, landmarks.landmark[i].y * h) for i in l_idx]
            right_pts = [(landmarks.landmark[i].x * w, landmarks.landmark[i].y * h) for i in r_idx]

            for pts in [left_pts, right_pts]:
                cv2.polylines(frame, [np.array(pts, dtype=np.int32)], True, (255, 255, 0), 1)

            ear_avg = (get_ear(left_pts) + get_ear(right_pts)) / 2.0
            if ear_avg < EAR_THRESHOLD:
                if eyes_closed_start is None: eyes_closed_start = time.time()
                if time.time() - eyes_closed_start > 2:
                    current_violation = "eyes"
            else:
                eyes_closed_start = None
            

            if use_gaze and not current_violation:
                pupil_x = landmarks.landmark[468].x 
                eye_left_x = landmarks.landmark[33].x
                eye_right_x = landmarks.landmark[133].x
                
                denom = (eye_right_x - eye_left_x)
                rel_pos = (pupil_x - eye_left_x) / (denom + 1e-6)

                if rel_pos < 0.35 or rel_pos > 0.65:
                    if gaze_lost_start is None: gaze_lost_start = time.time()
                    if time.time() - gaze_lost_start > 2:
                        current_violation = "gaze"
                else:
                    gaze_lost_start = None
        else:
            if face_lost_start is None: face_lost_start = time.time()
            if time.time() - face_lost_start > 1.5:
                current_violation = "face"

        if current_violation and violation_img is not None:
            if not violation_active:
                cv2.imshow("Violation_Alert", violation_img)
                violation_active = True
        else:
            if violation_active:
                try:
                    cv2.destroyWindow("Violation_Alert")
                except:
                    pass
                violation_active = False
    

        time_left = max(0, int(run_duration - elapsed))
        h_left, m_left, s_left = time_left // 3600, (time_left % 3600) // 60, time_left % 60
        timer_text = f"Time left: {h_left:02}:{m_left:02}:{s_left:02}"
        
        cv2.putText(frame, timer_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        cv2.imshow("Monitoring (User #1)", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    run_monitor()
