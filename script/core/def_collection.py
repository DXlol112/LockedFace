import sys
import cv2
import json
import mediapipe as mp
import os

def load_config(config_path='config.json'):
    try:
        with open(config_path, "r", encoding='utf-8') as f:
            data = json.load(f)
            
            file = data["selected_file"]
            gaze = data["gaze_enabled"]
            glasses_enabled = data["glasses_enabled"]
            work_time = data["work_time_seconds"] # in seconds

            return file, gaze, glasses_enabled, work_time 
    except Exception as e:
        print(f"Ошибка загрузки{e}")
        return sys.exit()

def main():
    file, gaze, glasses_enabled, work_time = load_config()


if __name__ in "__main__":
    main()
        
    
    