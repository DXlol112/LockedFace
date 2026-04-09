from PyQt6.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QCheckBox, QDialog, QFrame
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QPixmap

import json
import requests
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
        info_block = QHBoxLayout()
        info_block.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.icon_project = QLabel()
        self.icon_project.setPixmap(QPixmap("static/icon/app_icon.png"))
        self.icon_project.setObjectName("icon_project")
        self.icon_project.setFixedSize(218, 218)
        self.icon_project.setScaledContents(True)

        text_block = QVBoxLayout()
        text_block.setSpacing(10)

        self.name = QLabel("Maintaining attention at work")
        self.name.setObjectName("name_set")
        self.name.setContentsMargins(0,40,0,0)

        self.ver = QLabel("Версия: 1.0.0")
        self.ver.setObjectName("ver_set")
        self.ver.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.ver.setContentsMargins(0,5,0,0)
        
        text_block.addWidget(self.name)
        text_block.addWidget(self.ver)
        text_block.addStretch()

        info_block.addSpacing(20)
        info_block.addWidget(self.icon_project)
        info_block.addSpacing(20)
        info_block.addLayout(text_block)
        info_block.addStretch()

        #----------------------actions-------------------------#
        actions_layout = QVBoxLayout()
        actions_layout.setSpacing(10)
        actions_layout.setContentsMargins(10,0,0,0)

        def create_action(text:str, icon_path:str, size: tuple, callback=None): #<div> text...........btn</div>
            row = QHBoxLayout()

            label = QLabel(text)
            label.setObjectName("text_settengs")

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

        chek_updates = create_action("Проверить обновление", "static/btn_icon/refresh_btn.png", (51,49), self.update_cheker)
        open_folder_text_btn  = create_action("Открыть рабочую папку", "static/btn_icon/link_btn.png",(56,46), self.open_folder)
        source_code = create_action("Исходный код","static/btn_icon/link_btn.png", (56,46), self.open_github)

        actions_layout.addLayout(chek_updates)
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
        toggle_layout.setContentsMargins(10,0,0,0)
        toggle_layout.setSpacing(10)

        def create_toggle(text:str, json_key:str, callback=None):
            row = QHBoxLayout()

            label = QLabel(text)
            label.setObjectName("text_settengs")

            togle = QCheckBox()
            togle.setObjectName("toggle_btn")
            
            current_state = self.load_state(json_key)
            togle.setChecked(current_state)

            togle.stateChanged.connect(lambda state: self.save_state(state == 2, json_key))

            row.addWidget(label)
            row.addStretch()
            row.addWidget(togle)

            return row
        
        togle_gaze = create_toggle("Включить отслеживание направление глаз (Pre Alpha)", "gaze_enabled")
        toggle_glasses = create_toggle("Наличие очков", "glasses_enabled")

        toggle_layout.addLayout(togle_gaze)
        toggle_layout.addSpacing(12)
        toggle_layout.addLayout(toggle_glasses)
    #----------------------ALL-------------------------#
        main_layout.addWidget(header_widget)
        main_layout.addLayout(info_block)
        main_layout.addLayout(actions_layout)

        main_layout.addSpacing(20)
        main_layout.addWidget(crate_line())

        main_layout.addSpacing(10)
        main_layout.addLayout(toggle_layout)
        main_layout.addStretch()

    #-------------------------Functions---------------------#   
    def update_cheker(self):
        pass
    
    def open_folder(self):
        project_path = Path(__file__).resolve().parent.parent.parent
        os.startfile(project_path)

    def open_github(self):
        webbrowser.open("https://github.com/DXlol112")


    def save_state(self, checked:bool, json_key:str):
        with open("config.json", "r", encoding="utf-8") as f:
            data = json.load(f)

        data[json_key] = checked

        with open("config.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    


    def load_state(self, json_key:str):
        with open("config.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get(json_key, False)


        


        
    


        