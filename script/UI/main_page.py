from PyQt6.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QRect, QSize
from PyQt6.QtGui import QIcon
import os
import json


class MainPage(QWidget):
    def __init__(self,on_start, on_settings, on_file):
        super().__init__()

        self.on_start = on_start
        self.on_settings = on_settings
        self.on_file = on_file
        self.config_path = "config.json"

        self.h = 0
        self.m = 0
        self.s = 0
        self.load_time_from_config() 
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
    
    #-------------------------header-------------------------------#  
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

        self.setting_btn.clicked.connect(on_settings)
        self.file_btn.clicked.connect(on_file)

        header.addStretch()
        header.addWidget(self.file_btn)
        header.addWidget(self.setting_btn)

        #-------------------timer-----------------------------------#
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

        #------------------Footer------------------------#
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

        #---------------ALL--------------------#
        main_layout.addWidget(header_widget)
        main_layout.addSpacing(10)
        main_layout.addLayout(time_layout)
        main_layout.addSpacing(20)
        main_layout.addLayout(footer)

        self.update_label()
        #--------------------------------------------#
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


    def create_arrow(self, text, func):
        btn = QPushButton(text)
        btn.setObjectName("arrow_btn")
        btn.clicked.connect(func)
        return btn

    def update_label(self):
        self.time_label.setText(f"{self.h:02}:{self.m:02}:{self.s:02}")

    #up
    def inc_h(self): self.h = (self.h + 1) % 24; self.update_label()
    def inc_m(self): self.m = (self.m + 1) % 60; self.update_label()
    def inc_s(self): self.s = (self.s + 1) % 60; self.update_label()

    #down
    def dec_h(self): self.h = (self.h - 1) % 24; self.update_label()
    def dec_m(self): self.m = (self.m - 1) % 60; self.update_label()
    def dec_s(self): self.s = (self.s - 1) % 60; self.update_label()

    #-------------------------------------#
    def start_clicked(self):
        self.save_time_to_config()
        self.animate_and_start()
        
    def animate_and_start(self):
        self.anim = QPropertyAnimation(self, b"geometry")
        self.anim.setDuration(500)

        start_rect = self.geometry()
        end_rect = QRect(start_rect.x(),start_rect.y() + 800, start_rect.width(),start_rect.height())

        self.anim.setStartValue(start_rect)
        self.anim.setEndValue(end_rect)

        self.anim.finished.connect(self.on_start)

        self.anim.start()

    
    
    