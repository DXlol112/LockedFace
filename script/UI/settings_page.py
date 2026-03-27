from PyQt6.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QRect, QSize
from PyQt6.QtGui import QIcon, QPixmap

class SettingsPage(QWidget):
    def __init__(self,main_page):
        super().__init__()

        self.main_page = main_page

        settings_layout = QHBoxLayout()

    #----------------Header---------------------#
        header_widget = QWidget()
        header_widget.setObjectName("header_sett")
        header_widget.setFixedHeight(60)

        header = QHBoxLayout(header_widget)

        self.back_btn = QPushButton()
        self.back_btn.setObjectName("back_btn")
        self.back_btn.setIcon(QIcon("static/btn_icon/back_btn.png"))
        self.back_btn.setIconSize(QSize(71, 48))

        header.addStretch()
        header.addWidget(self.back_btn)
    
        #---------------info-----------------#
        info_layout = QHBoxLayout()

        icon_ver= QHBoxLayout()
        info_project = QHBoxLayout()

        self.icon_project = QLabel()
        self.icon_project.setPixmap(QPixmap("static/icon/app_icon.png"))
        self.icon_project.setObjectName("icon_project")
        self.icon_project.setFixedSize(218, 218)

        self.name = QLabel("Maintaining attention at work")
        self.name.setObjectName("name")

        self.ver = QLabel("Версия: 1.0.0")
        self.ver.setObjectName("ver")
    
        

    


        