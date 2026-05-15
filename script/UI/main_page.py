import os
import json
import cv2
import numpy as np

from PyQt6.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QSizePolicy
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QRect, QSize, pyqtSlot
from PyQt6.QtGui import QIcon, QImage, QPixmap

from script.core.def_collection import VideoThread 

class MainPage(QWidget):
    def __init__(self, on_start, on_settings, on_file):
        super().__init__()
        
        self.on_start_callback = on_start
        self.on_settings = on_settings
        self.on_file = on_file
        self.config_path = "config.json"

        self.h = 0
        self.m = 0
        self.s = 0
        self.load_time_from_config() 
        
        self.timer_widget = QWidget(self)
        self.setup_timer_ui()

        self.video_widget = QWidget(self)
        self.setup_video_ui()
        self.video_widget.hide()

        self.thread = None # type: ignore

    def setup_timer_ui(self):
        main_layout = QVBoxLayout(self.timer_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
    
        header_widget = QWidget()
        header_widget.setObjectName("header")
        header_widget.setFixedHeight(60)
        header = QHBoxLayout(header_widget)

        self.file_btn = QPushButton()
        self.file_btn.setObjectName("icon_btn")
        self.file_btn.setIcon(QIcon("static/btn_icon/file_path.png"))
        self.file_btn.setIconSize(QSize(53, 53))
        
        self.setting_btn = QPushButton()
        self.setting_btn.setObjectName("icon_btn")
        self.setting_btn.setIcon(QIcon("static/btn_icon/setting.png"))
        self.setting_btn.setIconSize(QSize(53, 53))

        self.setting_btn.clicked.connect(self.on_settings)
        self.file_btn.clicked.connect(self.on_file)

        header.addStretch()
        header.addWidget(self.file_btn)
        header.addWidget(self.setting_btn)

        time_layout = QVBoxLayout()
        time_layout.setSpacing(5)
        time_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        arrows_top = QHBoxLayout()
        timer_box = QHBoxLayout()
        arrows_bottom = QHBoxLayout()

        self.up_h = self.create_arrow("▲", self.inc_h)
        self.up_m = self.create_arrow("▲", self.inc_m)
        self.up_s = self.create_arrow("▲", self.inc_s)

        arrows_top.addWidget(self.up_h)
        arrows_top.addWidget(self.up_m)
        arrows_top.addWidget(self.up_s)

        self.time_label = QLabel("00:00:00")
        timer_box.addWidget(self.time_label, alignment=Qt.AlignmentFlag.AlignCenter)
        self.time_label.setObjectName("timer")

        self.down_h = self.create_arrow("▼", self.dec_h)
        self.down_m = self.create_arrow("▼", self.dec_m)
        self.down_s = self.create_arrow("▼", self.dec_s)

        arrows_bottom.addWidget(self.down_h)
        arrows_bottom.addWidget(self.down_m)
        arrows_bottom.addWidget(self.down_s)

        time_layout.addLayout(arrows_top)
        time_layout.addLayout(timer_box)
        time_layout.addLayout(arrows_bottom)

        footer = QVBoxLayout()
        footer.setSpacing(0)
        footer.setContentsMargins(0,0,0,10)

        self.start_btn = QPushButton("СТАРТ")
        self.start_btn.setObjectName("start_btn")
        self.start_btn.clicked.connect(self.start_clicked)
        
        self.info = QLabel("Перед началом выберете файл")
        self.info.setObjectName("text_info_file")
        self.info.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.ver = QLabel("Версия: 1.0.0")
        self.ver.setObjectName("ver")
        self.ver.setAlignment(Qt.AlignmentFlag.AlignCenter)

        footer.addWidget(self.start_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        footer.addWidget(self.info)
        footer.addStretch()
        footer.addWidget(self.ver)

        main_layout.addWidget(header_widget)
        main_layout.addSpacing(10)
        main_layout.addLayout(time_layout)
        main_layout.addSpacing(20)
        main_layout.addLayout(footer)

        self.update_label()

    def setup_video_ui(self):
        video_layout = QVBoxLayout(self.video_widget)
        video_layout.setContentsMargins(20, 20, 20, 20)
        video_layout.setSpacing(20)

        self.video_label = QLabel("")
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_label.setStyleSheet("background-color: transparent;")
        self.video_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        btn_layout = QHBoxLayout()
        
        self.pause_btn = QPushButton("Пауза")
        self.pause_btn.setFixedSize(100, 100)
        self.pause_btn.setStyleSheet("""
            QPushButton {
                background-color: #d9d9d9;
                color: black;
                border-radius: 50px;
                font-size: 16px;
            }
        """)
        self.pause_btn.clicked.connect(self.toggle_pause)

        self.stop_btn = QPushButton("Стоп")
        self.stop_btn.setFixedSize(100, 100)
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff0000;
                color: white;
                border-radius: 50px;
                font-size: 16px;
            }
        """)
        self.stop_btn.clicked.connect(self.stop_video_manual)

        btn_layout.addStretch()
        btn_layout.addWidget(self.pause_btn)
        btn_layout.addSpacing(50)
        btn_layout.addWidget(self.stop_btn)
        btn_layout.addStretch()

        video_layout.addWidget(self.video_label)
        video_layout.addLayout(btn_layout)

    def resizeEvent(self, event): # type: ignore
        self.timer_widget.resize(self.width(), self.height())
        self.video_widget.resize(self.width(), self.height())
        super().resizeEvent(event)

    def load_time_from_config(self):
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    t = config.get("work_time_seconds", 0)
                    self.h, self.m, self.s = t // 3600, (t % 3600) // 60, t % 60
        except: pass
    
    def save_time_to_config(self):
        total = self.h * 3600 + self.m * 60 + self.s
        config = {}
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f: config = json.load(f)
            except: pass
        config["work_time_seconds"] = total
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)

    def get_full_config(self):
        try:
            with open(self.config_path, "r", encoding='utf-8') as f:
                data = json.load(f)
                return data.get("selected_file", ""), data.get("gaze_enabled", False), data.get("glasses_enabled", False)
        except Exception:
            return "", False, False

    def create_arrow(self, text, func):
        btn = QPushButton(text)
        btn.setObjectName("arrow_btn")
        btn.clicked.connect(func)
        return btn

    def update_label(self):
        self.time_label.setText(f"{self.h:02}:{self.m:02}:{self.s:02}")

    def inc_h(self): self.h = (self.h + 1) % 24; self.update_label()
    def inc_m(self): self.m = (self.m + 1) % 60; self.update_label()
    def inc_s(self): self.s = (self.s + 1) % 60; self.update_label()

    def dec_h(self): self.h = (self.h - 1) % 24; self.update_label()
    def dec_m(self): self.m = (self.m - 1) % 60; self.update_label()
    def dec_s(self): self.s = (self.s - 1) % 60; self.update_label()

    def start_clicked(self):
        self.save_time_to_config()
        self.animate_and_start()
        
    def animate_and_start(self):
        self.anim = QPropertyAnimation(self.timer_widget, b"geometry")
        self.anim.setDuration(500)

        start_rect = self.timer_widget.geometry()
        end_rect = QRect(start_rect.x(), start_rect.y() + self.height(), start_rect.width(), start_rect.height())

        self.anim.setStartValue(start_rect)
        self.anim.setEndValue(end_rect)
        self.anim.finished.connect(self.start_video_process)
        self.anim.start()

    def start_video_process(self):
        self.timer_widget.hide()
        self.video_widget.show()
        
        file_path, gaze, glasses = self.get_full_config()
        total_time = self.h * 3600 + self.m * 60 + self.s

        self.thread = VideoThread(file_path, gaze, glasses, total_time) # type: ignore
        self.thread.change_pixmap_signal.connect(self.update_video_image) # type: ignore
        self.thread.finished_signal.connect(self.on_video_finished) # type: ignore
        self.thread.start() # type: ignore
        
        if self.on_start_callback:
            self.on_start_callback()

    @pyqtSlot(np.ndarray)
    def update_video_image(self, cv_img):
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        qt_img = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_img).scaled(
            self.video_label.width(), self.video_label.height(), 
            Qt.AspectRatioMode.KeepAspectRatio
        )
        self.video_label.setPixmap(pixmap)

    def toggle_pause(self):
        if self.thread:
            self.thread.toggle_pause() # type: ignore
            if self.thread.is_paused: # type: ignore
                self.pause_btn.setText("Продолжить")
            else:
                self.pause_btn.setText("Пауза")

    def stop_video_manual(self):
        if self.thread:
            self.thread.stop() # type: ignore

    def on_video_finished(self):
        self.video_widget.hide()
        self.timer_widget.show()
        
        self.video_label.clear()
        self.pause_btn.setText("Пауза")

        self.anim = QPropertyAnimation(self.timer_widget, b"geometry")
        self.anim.setDuration(500)

        start_rect = QRect(0, self.height(), self.width(), self.height())
        end_rect = QRect(0, 0, self.width(), self.height())

        self.anim.setStartValue(start_rect)
        self.anim.setEndValue(end_rect)
        self.anim.start()
