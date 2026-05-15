from PyQt6.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QCheckBox, QDialog, QFrame, QGridLayout
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QPixmap

import json
import webbrowser
from pathlib import Path
import os


class SettingsPage(QWidget):
    def __init__(self, on_back):
        super().__init__()

        self.on_back = on_back

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

    #----------------Header---------------------#
        header_widget = QWidget()
        header_widget.setObjectName("header_sett")
        header_widget.setFixedHeight(60)

        header = QHBoxLayout(header_widget)

        self.back_btn = QPushButton()
        self.back_btn.setObjectName("back_btn")
        self.back_btn.setIcon(QIcon("static/btn_icon/back_btn.png"))
        self.back_btn.setIconSize(QSize(71, 48))
        
        self.back_btn.clicked.connect(self.on_back)
        
        header.addWidget(self.back_btn)
        header.addStretch()
        #---------------info-----------------#
        info_block = QGridLayout()
        info_block.setContentsMargins(0, 0, 0, 0)
        info_block.setSpacing(0)

        self.icon_project = QLabel()
        self.icon_project.setPixmap(QPixmap("static/icon/logo_icon.svg"))
        self.icon_project.setObjectName("icon_project")
        self.icon_project.setFixedSize(218, 218)
        self.icon_project.setScaledContents(True)

        text_block = QVBoxLayout()
        text_block.setSpacing(10)

        self.name = QLabel("LockedFace")
        self.name.setObjectName("name_set")
        self.name.setContentsMargins(0, 0, 0, 0)
        self.name.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.ver = QLabel("Версия: 1.0.0")
        self.ver.setObjectName("ver_set")
        self.ver.setContentsMargins(0, 0, 0, 0)
        self.ver.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        text_block.addWidget(self.name)
        text_block.addWidget(self.ver)

        info_block.addWidget(self.icon_project, 0, 0, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        info_block.addLayout(text_block, 0, 1, Qt.AlignmentFlag.AlignCenter)
        
        spacer_right = QWidget()
        spacer_right.setFixedWidth(218)
        info_block.addWidget(spacer_right, 0, 2)

        info_block.setColumnStretch(0, 0)
        info_block.setColumnStretch(1, 1)
        info_block.setColumnStretch(2, 0)

        #----------------------actions-------------------------#
        actions_layout = QVBoxLayout()
        actions_layout.setSpacing(10)
        actions_layout.setContentsMargins(10, 0, 0, 0)

        def create_action(text:str, icon_path:str, size: tuple, callback=None): #<div> text...........btn</div>
            row = QHBoxLayout()

            label = QLabel(text)
            label.setObjectName("text_settings")

            btn = QPushButton()
            btn.setObjectName("settings_btn")
            btn.setIcon(QIcon(icon_path))
            btn.setIconSize(QSize(*size))

            if callback:
                btn.clicked.connect(callback)
            
            row.addWidget(label)
            row.addStretch()
            row.addWidget(btn)

            return row

        check_updates = create_action("Проверить обновление", "static/btn_icon/refresh_btn.png", (51, 49), self.update_checker)
        open_folder_text_btn  = create_action("Открыть рабочую папку", "static/btn_icon/link_btn.png", (56, 46), self.open_folder)
        source_code = create_action("Исходный код", "static/btn_icon/link_btn.png", (56, 46), self.open_github)

        actions_layout.addLayout(check_updates)
        actions_layout.addLayout(open_folder_text_btn)
        actions_layout.addLayout(source_code)
    #------------------line sep-------------------------#
        def crate_line():    
            line = QFrame()
            line.setFrameShape(QFrame.Shape.HLine)
            line.setFrameShadow(QFrame.Shadow.Sunken)
            line.setObjectName("line_sep")
            line.setFixedHeight(1)
            return line
        
    #-------------------------Toggle---------------------#
        toggle_layout = QVBoxLayout()
        toggle_layout.setContentsMargins(10, 0, 5, 0)
        toggle_layout.setSpacing(10)

        def create_toggle(text:str, json_key:str, callback=None):
            row = QHBoxLayout()

            label = QLabel(text)
            label.setObjectName("text_settings")

            toggle = QCheckBox()
            toggle.setObjectName("toggle_btn")
            
            current_state = self.load_state(json_key)
            toggle.setChecked(current_state)

            toggle.stateChanged.connect(lambda state: self.save_state(state == 2, json_key))

            row.addWidget(label)
            row.addStretch()
            row.addWidget(toggle)

            return row
        
        toggle_gaze = create_toggle("Включить отслеживание глаз ", "gaze_enabled")
        toggle_glasses = create_toggle("Наличие очков", "glasses_enabled")

        toggle_layout.addLayout(toggle_gaze)
        toggle_layout.addSpacing(12)
        toggle_layout.addLayout(toggle_glasses)
    #----------------------ALL-------------------------#
        main_layout.addWidget(header_widget)
        main_layout.addSpacing(3)
        main_layout.addLayout(info_block)
        main_layout.addSpacing(20)

        main_layout.addLayout(actions_layout)

        main_layout.addSpacing(20)
        main_layout.addWidget(crate_line())

        main_layout.addSpacing(10)
        main_layout.addLayout(toggle_layout)
        main_layout.addStretch()

    #-------------------------Functions---------------------#   
    DEFAULT_CONFIG = {
        "selected_file": None,
        "gaze_enabled": False,
        "glasses_enabled": False,
        "work_time_seconds": 0
    }
    
    def update_checker(self):
        pass
    
    def open_folder(self):
        project_path = Path(__file__).resolve().parent.parent.parent
        os.startfile(project_path)

    def open_github(self):
        webbrowser.open("github.com")

    def save_state(self, checked: bool, json_key: str):
        data = self.DEFAULT_CONFIG.copy()
        if os.path.exists("config.json"):
            try:
                with open("config.json", "r", encoding="utf-8") as f:
                    data = json.load(f)
            except (json.JSONDecodeError, IOError):
                pass

        data[json_key] = checked

        try:
            with open("config.json", "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except IOError as e:
            print(f"Ошибка записи конфига: {e}")

    def load_state(self, json_key: str):
        if not os.path.exists("config.json"):
            try:
                with open("config.json", "w", encoding="utf-8") as f:
                    json.dump(self.DEFAULT_CONFIG, f, indent=4, ensure_ascii=False)
            except IOError:
                pass
            return self.DEFAULT_CONFIG.get(json_key, False)

        try:
            with open("config.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get(json_key, self.DEFAULT_CONFIG.get(json_key, False))
        except (json.JSONDecodeError, IOError):
            return self.DEFAULT_CONFIG.get(json_key, False)
