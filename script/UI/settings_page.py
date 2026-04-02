from PyQt6.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QCheckBox, QDialog
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QPixmap

import json
import requests
import webbrowser
from pathlib import Path


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

        self.icon_project = QLabel()
        self.icon_project.setPixmap(QPixmap("static/icon/app_icon.png"))
        self.icon_project.setObjectName("icon_project")
        self.icon_project.setFixedSize(218, 218)

        text_block = QVBoxLayout()

        self.name = QLabel("Maintaining attention at work")
        self.name.setObjectName("name_set")

        self.ver = QLabel("Версия: 1.0.0")
        self.ver.setObjectName("ver_set")
        
        text_block.addWidget(self.name)
        text_block.addWidget(self.ver)

        info_block.addSpacing(20)
        info_block.addWidget(self.icon_project)
        info_block.addSpacing(20)
        info_block.addLayout(text_block)
        info_block.addStretch()

        #----------------------actions-------------------------#
        actions_layout = QVBoxLayout()

        self.update_text = QLabel("Проверить обновление")
        self.update_text.setObjectName("text_settengs")    
        
        self.update_btn = QPushButton()
        self.update_btn.setIcon(QIcon("static/btn_icon/refresh_btn.png"))
        
        self.folder_text = QLabel("Открыть рабочую папку")
        self.folder_text.setObjectName("text_settengs")

        self.folder_btn = QPushButton()
        self.folder_btn.setIcon(QIcon("static/btn_icon/link_btn.png"))
    
        self.github_text = QLabel("Исходный код")
        self.github_text.setObjectName("text_settengs")

        self.github_btn = QPushButton()
        self.github_btn.setIcon(QIcon("static/btn_icon/link_btn.png"))

        for btn in [self.update_btn, self.folder_btn, self.github_btn]:
            btn.setObjectName("settings_btn")

        actions_layout.addWidget(self.update_text)
        actions_layout.addWidget(self.update_btn)
        actions_layout.addWidget(self.folder_text)
        actions_layout.addWidget(self.folder_btn)
        actions_layout.addWidget(self.github_text)
        actions_layout.addWidget(self.github_btn)
    #-------------------------Toggle---------------------#
        toggle_layout = QVBoxLayout()

        self.gaze_label = QLabel("Включить отслеживание взгляда")
        self.gaze_label.setObjectName("text_settengs")

        self.toggle_btn = QCheckBox()
        self.toggle_btn.setObjectName("toggle_btn")
        self.toggle_btn.setCheckable(True)
        self.toggle_btn.stateChanged.connect(self.toggle_gaze)

        toggle_layout.addWidget(self.gaze_label)
        toggle_layout.addStretch()
        toggle_layout.addWidget(self.toggle_btn)

    #----------------------ALL-------------------------#
        main_layout.addWidget(header_widget)
        main_layout.addSpacing(20)
        main_layout.addLayout(info_block)
        main_layout.addSpacing(30)
        main_layout.addLayout(actions_layout)
        main_layout.addSpacing(30)
        main_layout.addLayout(toggle_layout)
        main_layout.addStretch()

    #-------------------------Functions---------------------#   
    def toggle_gaze(self):
        state = self.toggle_btn.isChecked()




class Overlay





def chek_update(current_version):
    #url = #URL_ПРОВЕРКИ_ОБНОВЛЕНИЙ
    
    try:
        r = requests.get(url, timeout=5)
        latest = r.json()["version"]
        
        return latest != current_version, latest
    except:
        return False, current_version

CONFIG_PATH = Path(__file__).resolve().parent.parent.parent / "config.json"

def load_config():
    if not CONFIG_PATH.exists():
        return {"version": "1.0.0", "gaze_enabled": False}

    with open(CONFIG_PATH, "r", encoding="utf-8") as f: 
        return json.load(f)
    
def save_config(data):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

        
    


        