import os
import sys
import time
import tempfile
import shutil
import cv2
import numpy as np

from .settings import (
    DEFAULT_SENSITIVITY,
    DEFAULT_TIMER_SETTINGS,
    LEFT_EYE_LANDMARKS,
    RIGHT_EYE_LANDMARKS,
    MonitoringTimers,
    SensitivitySettings,
    TimerSettings,
    is_eye_open,
    is_head_turned_away,
    run_detection_checks,
)

# Отключение аппаратного ускорения видео
os.environ['QT_XCB_GL_INTEGRATION'] = 'none'
os.environ['QT_DEBUG_PLUGINS'] = '0'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

from PyQt6.QtCore import QThread, pyqtSignal
from ffpyplayer.player import MediaPlayer

try:
    import mediapipe.solutions.face_mesh as mp_face_mesh # type: ignore
except ImportError:
    try:
        from mediapipe.python.solutions import face_mesh as mp_face_mesh
    except ImportError:
        sys.exit("Ошибка: подключения mediapipe")

def get_safe_path(orig_path):
    if not orig_path or not os.path.exists(orig_path): return None
    _, ext = os.path.splitext(orig_path)
    fd, temp_path = tempfile.mkstemp(suffix=ext)
    os.close(fd)
    shutil.copy2(orig_path, temp_path)
    return temp_path

class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(np.ndarray)
    finished_signal = pyqtSignal()

    def __init__(
        self,
        file,
        gaze,
        glasses_enabled,
        work_time,
        sensitivity: SensitivitySettings = DEFAULT_SENSITIVITY,
        timer_settings: TimerSettings = DEFAULT_TIMER_SETTINGS,
    ):
        super().__init__()
        self.file = file
        self.gaze = gaze
        self.glasses_enabled = glasses_enabled
        self.work_time = work_time
        self.sensitivity = sensitivity
        self.timer_settings = timer_settings
        
        self._run_flag = True
        self.is_paused = False

    def run(self):
        self._run_flag = True
        temp_name = get_safe_path(self.file)
        cap = cv2.VideoCapture(0)
        
        face_mesh = mp_face_mesh.FaceMesh(
            max_num_faces=1, 
            refine_landmarks=True, 
            min_detection_confidence=self.sensitivity.face_detection_confidence,
            min_tracking_confidence=self.sensitivity.face_tracking_confidence,
        )

        error_player = None
        error_cap = None
        
        error_window_active = False
        timers = MonitoringTimers(session_started_at=time.time())

        try:
            while cap.isOpened() and self._run_flag:
                curr_t = time.time()

                if self.is_paused:
                    if timers.pause_started_at is None:
                        timers.begin_pause(curr_t)
                        if error_player: error_player.set_pause(True)
                    
                    ret, frame = cap.read()
                    if ret:
                        cv2.putText(frame, "PAUSE", (50, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 2)
                        self.change_pixmap_signal.emit(frame)
                    time.sleep(self.timer_settings.pause_frame_delay)
                    continue
                else:
                    if timers.pause_started_at is not None:
                        timers.end_pause(curr_t)
                        if error_player: error_player.set_pause(False)

                ret, frame = cap.read()
                if not ret: break

                if timers.is_work_time_finished(curr_t, self.work_time):
                    print("Конец рабочего времени")
                    break

                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = face_mesh.process(rgb_frame)

                detection_status, landmarks = run_detection_checks(
                    results,
                    self.gaze,
                    self.glasses_enabled,
                    self.sensitivity,
                )

                if landmarks is not None:
                    for idx in LEFT_EYE_LANDMARKS + RIGHT_EYE_LANDMARKS:
                        pt = landmarks[idx]
                        cv2.circle(frame, (int(pt.x * frame.shape[1]), int(pt.y * frame.shape[0])), 2, (0, 255, 0), -1)

                should_error = timers.should_show_alert(
                    detection_status, curr_t, self.timer_settings
                )
                    
                if should_error:
                    if not error_window_active:
                        if temp_name:
                            ext = os.path.splitext(temp_name)[1].lower()
                            if ext in ['.jpg', '.jpeg', '.png']:
                                error_cap = None 
                            else:
                                try:
                                    error_player = MediaPlayer(temp_name)
                                    error_cap = cv2.VideoCapture(temp_name)
                                    if not error_cap.isOpened():
                                        print("Предупреждение: Не удалось открыть видеофайл, используется статичное изображение")
                                        error_cap = None
                                        if error_player:
                                            error_player.close_player()
                                            error_player = None
                                except Exception as e:
                                    print(f"Предупреждение: Ошибка при загрузке видеофайл: {e}")
                                    error_player = None
                                    error_cap = None
                            error_window_active = True
                        else:
                            print("Ошибка: Файл для Error_window нет")
                            continue

                    if error_cap:
                        try:
                            res, e_frame = error_cap.read()
                            audio_frame, val = error_player.get_frame() if error_player else (None, 0)
                        except Exception as e:
                            print(f"Предупреждение: Ошибка при чтении видеокадра: {e}")
                            res = False
                        
                        if not res:
                            error_cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                            res, e_frame = error_cap.read()

                        if val != 'eof' and isinstance(val, (int, float)) and val > 0: # type: ignore
                            current_video_time = error_cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0
                            wait_time = val - current_video_time
                            if wait_time > 0:
                                time.sleep(wait_time)

                        cv2.imshow("Error", e_frame) # type: ignore
                    else:
                        img = cv2.imread(temp_name) # type: ignore
                        if img is not None: cv2.imshow("Error", img)
                        
                elif error_window_active:
                    if error_player: error_player.close_player(); error_player = None
                    if error_cap: error_cap.release(); error_cap = None
                    try: cv2.destroyWindow("Error")
                    except: pass
                    error_window_active = False
                    timers.start_cooldown(curr_t, self.timer_settings)

                self.change_pixmap_signal.emit(frame)
                cv2.waitKey(1)

        finally:
            if error_player: error_player.close_player()
            if error_cap: error_cap.release()
            cap.release()
            try: cv2.destroyAllWindows()
            except: pass
            if temp_name and os.path.exists(temp_name):
                try: os.remove(temp_name)
                except: pass

            self.finished_signal.emit()

    def stop(self):
        self._run_flag = False
        self.wait()

    def toggle_pause(self):
        self.is_paused = not self.is_paused
