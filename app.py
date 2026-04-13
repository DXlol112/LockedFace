import sys
from PyQt6.QtWidgets import QApplication, QStackedWidget, QMainWindow
from PyQt6.QtGui import QIcon
from pathlib import Path

from script.UI.start_page import StartPage
from script.UI.main_page import MainPage
from script.UI.settings_page import SettingsPage
from script.UI.file_page import FilePage

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Maintaining attention at work")
        self.setWindowIcon(QIcon("static/icon/app_icon.png"))
        self.setFixedSize(800, 600)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.start_page = StartPage(self.go_to_main)
        self.main_page = MainPage(self.start_program, self.go_to_settings, self.go_to_file)
        self.settings_page = SettingsPage(self.go_back)
        self.file_page = FilePage(self.go_back)

        self.stack.addWidget(self.start_page)
        self.stack.addWidget(self.main_page)
        self.stack.addWidget(self.settings_page)
        self.stack.addWidget(self.file_page)

    def go_to_main(self):
        self.stack.setCurrentWidget(self.main_page)

    def go_to_settings(self):
        self.stack.setCurrentWidget(self.settings_page)

    def go_to_file(self):
        self.stack.setCurrentWidget(self.file_page)
    
    def go_back(self):
        if self.stack.currentWidget() == self.file_page:
            self.file_page.reset_delete_button()
            self.file_page.refresh_gallery()
        
        self.stack.setCurrentWidget(self.main_page)

    def start_program(self):
        print("Start program")

def load_stylesheet(app):
    with open(Path(__file__).resolve().parent / "script/style/all_project.qss", "r") as f:
        app.setStyleSheet(f.read())


def main():
    app = QApplication(sys.argv)

    load_stylesheet(app)

    window = MainWindow()
    window.show()

    app.exec()

if __name__ == "__main__":
    main()