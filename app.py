import sys
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QWidget,QLabel, QVBoxLayout
from script.scr.def_collection import *

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

        self.label = QLabel("Здесь будет тескт")
        self.label.setFont(QFont('Arial', 16))
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.button = QPushButton("Продолжить")
        self.button.setFixedSize(200,50)

        layout.addWidget(self.label)
        layout.addWidget(self.button, alignment=Qt.AlignmentFlag.AlignCenter)

app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()