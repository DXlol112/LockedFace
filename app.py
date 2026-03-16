import sys
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QWidget,QLabel, QVBoxLayout
from script.scr.def_collection import *
import numpy as np
import pathlib as pl
import cv2
import time
import shutil


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Maintaining attention at work")
        self.setWindowIcon(QIcon("icon/app_icon.jpg"))
        self.setFixedSize(QSize(800, 600))

        container = QWidget()
        self.setCentralWidget(container)

        layout = QVBoxLayout()
        container.setLayout(layout)

        self.label = QLabel("Перед использованием программы\n " \
        "Настройте камеру и освещение так, чтобы ваше лицо было хорошо видно." \
        "Поставьте камеру прямо перед собой на уровне глаз, " \
        "направьте её ровно на лицо и убедитесь, " \
        "что освещение достаточно яркое, чтобы ваше лицо было хорошо видно. Избегайте сильного контрового света и теней на лице.")
        
        self.label.setFont(QFont('Arial', 16))
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.button = QPushButton("Продолжить")
        self.button.setFixedSize(200,50)

        layout.addWidget(self.label)
        layout.addWidget(self.button, alignment=Qt.AlignmentFlag.AlignCenter)

def load_stylesheet(app):
    with open("script/style/MainWindow.qss", "r") as f:
        app.setStyleSheet(f.read())


app = QApplication(sys.argv)

load_stylesheet(app)

window = MainWindow()
window.show()

app.exec()