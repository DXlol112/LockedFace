"""Application entry point."""

from __future__ import annotations

import logging
import multiprocessing
import os
import sys
import traceback
from pathlib import Path

# These variables must be set before importing Qt or MediaPipe.
os.environ["QT_XCB_GL_INTEGRATION"] = "none"
os.environ["QT_DEBUG_PLUGINS"] = "0"

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget

from script import FilePage, MainPage, SettingsPage, StartPage, get_application_dir, get_log_dir
from script.core.i18n import install_translation
from script.core.logger import setup_logging


logger = logging.getLogger(__name__)
APP_NAME = "LockedFace"


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle(APP_NAME)
        self.setWindowIcon(QIcon("static/icon/logo_icon.ico"))
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

    def go_to_main(self) -> None:
        self.stack.setCurrentWidget(self.main_page)

    def go_to_settings(self) -> None:
        self.stack.setCurrentWidget(self.settings_page)

    def go_to_file(self) -> None:
        self.stack.setCurrentWidget(self.file_page)

    def go_back(self) -> None:
        if self.stack.currentWidget() is self.file_page:
            self.file_page.reset_delete_button()
            self.file_page.refresh_gallery()

        self.stack.setCurrentWidget(self.main_page)

    def start_program(self) -> None:
        logger.info("Video monitoring started")


def load_stylesheet(app: QApplication) -> None:
    stylesheet_dir = Path("script/style")
    stylesheet_files = (
        "start_page.qss",
        "main_page.qss",
        "settings_page.qss",
        "file_page.qss",
    )
    stylesheet = "\n".join(
        (stylesheet_dir / filename).read_text(encoding="utf-8")
        for filename in stylesheet_files
    )
    app.setStyleSheet(stylesheet)


def main() -> int:
    multiprocessing.freeze_support()
    os.chdir(get_application_dir())

    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setOrganizationName(APP_NAME)

    setup_logging()
    # Keep a reference for the whole lifetime of the application.
    app.translator = install_translation(app)  # type: ignore[attr-defined]

    load_stylesheet(app)

    window = MainWindow()
    window.show()
    logger.info("%s started", APP_NAME)

    return app.exec()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        crash_log = get_log_dir() / "crash.log"
        crash_log.write_text(traceback.format_exc(), encoding="utf-8")
        logging.getLogger(__name__).exception("Unexpected application shutdown")
        raise
