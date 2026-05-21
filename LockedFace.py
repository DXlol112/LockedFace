import os
# Отключение аппаратного ускорения видео 
os.environ['QT_XCB_GL_INTEGRATION'] = 'none'
os.environ['QT_DEBUG_PLUGINS'] = '0'
import traceback
import sys
import logging
from PyQt6.QtWidgets import QApplication, QStackedWidget, QMainWindow
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import qInstallMessageHandler, QtMsgType
from pathlib import Path

from script import (
    StartPage,
    MainPage,
    SettingsPage,
    FilePage,
    get_resource_path,
    get_log_dir
)

class LoggingFile:
    def __init__(self, logger, log_level) -> None:
        self.logger = logger
        self.log_level = log_level
        self._buffer = []

    def write(self, buf):
        self._buffer.append(buf)
        
        if "\n" in buf:
            full_text = "".join(self._buffer)
            self._buffer.clear()
            
            lines = full_text.splitlines(keepends=True)
            for line in lines:
                if line.endswith("\n"):
                    cleaned = line.strip()
                    if cleaned:
                        self.logger.log(self.log_level, cleaned)
                else:
                    self._buffer.append(line)
            
    def flush(self):
        if self._buffer:
            cleaned = "".join(self._buffer).strip()
            if cleaned:
                self.logger.log(self.log_level, cleaned)
            self._buffer.clear()

def qt_message_handler(mode, context, message):
    logger = logging.getLogger("Qt")
    if mode == QtMsgType.QtDebugMsg:
        logger.debug(message)
    elif mode == QtMsgType.QtInfoMsg:
        logger.info(message)
    elif mode == QtMsgType.QtWarningMsg:
        logger.warning(message)
    elif mode == QtMsgType.QtCriticalMsg:
        logger.error(message)
    elif mode == QtMsgType.QtFatalMsg:
        logger.critical(message)

def setup_logging():
    log_dir = get_log_dir()
    log_file = log_dir / "app.log"

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - [%(levelname)s] - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8", mode="w"),
            logging.StreamHandler(sys.__stdout__)
        ]
    )

    logging.captureWarnings(True)
    logging.getLogger("py.warnings").setLevel(logging.CRITICAL)
    logging.getLogger("google").setLevel(logging.ERROR)
    logging.getLogger("mediapipe").setLevel(logging.ERROR)

    root_logger = logging.getLogger()
    sys.stdout = LoggingFile(root_logger, logging.INFO)
    sys.stderr = LoggingFile(root_logger, logging.ERROR)
    
    qInstallMessageHandler(qt_message_handler)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("LockedFace")
        self.setWindowIcon(QIcon(str(get_resource_path("static/icon/logo_icon.ico"))))
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
    stylesheet_path = get_resource_path("script/style/all_project.qss")
    with open(stylesheet_path, "r", encoding="utf-8") as f:
        app.setStyleSheet(f.read())


def main():
    import multiprocessing
    multiprocessing.freeze_support()
    
    setup_logging()
    print("Start LockedFace")

    app = QApplication(sys.argv)

    load_stylesheet(app)

    window = MainWindow()
    window.show()

    app.exec()
    print("close LockedFace")
    
    sys.stdout.flush()
    sys.stderr.flush()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log_dir = get_log_dir()
        crash_log = log_dir / "crash.log"
        with open(crash_log, "w", encoding="utf-8") as f:
            f.write(traceback.format_exc())
