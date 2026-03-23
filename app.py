import sys
from PyQt6.QtWidgets import QApplication, QStackedWidget, QMainWindow
from PyQt6.QtGui import QIcon
from pathlib import Path

from script.UI.start_page import StartPage
from script.UI.main_page import MainPage

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Maintaining attention at work")
        self.setWindowIcon(QIcon("static/icon/app_icon.png"))
        self.setFixedSize(800, 600)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.start_page = StartPage(self.go_to_main)
        self.main_page = MainPage(self.start_program)

        self.stack.addWidget(self.start_page)
        self.stack.addWidget(self.main_page)

    def go_to_main(self):
        self.stack.setCurrentWidget(self.main_page)

    def start_program(self):
        print("Start program")

def load_stylesheet(app):
    
    with open(Path(__file__).resolve().parent / "script/style/MainWindow.qss", "r") as f:
        app.setStyleSheet(f.read())

app = QApplication(sys.argv)

load_stylesheet(app)

window = MainWindow()
window.show()

app.exec()