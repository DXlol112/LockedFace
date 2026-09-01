from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
from PyQt6.QtCore import QEvent, QPropertyAnimation, QRect, QSize, Qt, pyqtSlot
from PyQt6.QtGui import QIcon, QImage, QPixmap
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from script.UI.support_UI import WinDialog
from script.core import VideoThread, __version__, load_config, update_config


class MainPage(QWidget):
    def __init__(self, on_start, on_settings, on_file) -> None:  # type: ignore[no-untyped-def]
        super().__init__()

        self.on_start_callback = on_start
        self.on_settings = on_settings
        self.on_file = on_file
        self.h = 0
        self.m = 0
        self.s = 0
        self.thread: VideoThread | None = None
        self._load_time_from_config()

        self.timer_widget = QWidget(self)
        self._setup_timer_ui()

        self.video_widget = QWidget(self)
        self._setup_video_ui()
        self.video_widget.hide()

        self.retranslate_ui()

    def _setup_timer_ui(self) -> None:
        main_layout = QVBoxLayout(self.timer_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)

        header_widget = QWidget()
        header_widget.setObjectName("header")
        header_widget.setFixedHeight(60)
        header = QHBoxLayout(header_widget)

        self.file_button = QPushButton()
        self.file_button.setObjectName("icon_btn")
        self.file_button.setIcon(QIcon("static/btn_icon/file_path.png"))
        self.file_button.setIconSize(QSize(53, 53))

        self.settings_button = QPushButton()
        self.settings_button.setObjectName("icon_btn")
        self.settings_button.setIcon(QIcon("static/btn_icon/setting.png"))
        self.settings_button.setIconSize(QSize(53, 53))

        self.settings_button.clicked.connect(self.on_settings)
        self.file_button.clicked.connect(self.on_file)

        header.addStretch()
        header.addWidget(self.file_button)
        header.addWidget(self.settings_button)

        time_layout = QVBoxLayout()
        time_layout.setSpacing(5)
        time_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        arrows_top = QHBoxLayout()
        timer_box = QHBoxLayout()
        arrows_bottom = QHBoxLayout()

        for callback in (self.inc_h, self.inc_m, self.inc_s):
            arrows_top.addWidget(self._create_arrow("▲", callback))

        self.time_label = QLabel("00:00:00")
        self.time_label.setObjectName("timer")
        timer_box.addWidget(self.time_label, alignment=Qt.AlignmentFlag.AlignCenter)

        for callback in (self.dec_h, self.dec_m, self.dec_s):
            arrows_bottom.addWidget(self._create_arrow("▼", callback))

        time_layout.addLayout(arrows_top)
        time_layout.addLayout(timer_box)
        time_layout.addLayout(arrows_bottom)

        footer = QVBoxLayout()
        footer.setSpacing(0)
        footer.setContentsMargins(0, 0, 0, 10)

        self.start_button = QPushButton()
        self.start_button.setObjectName("start_btn")
        self.start_button.clicked.connect(self.start_clicked)

        self.info_label = QLabel()
        self.info_label.setObjectName("text_info_file")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.version_label = QLabel()
        self.version_label.setObjectName("ver")
        self.version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        footer.addWidget(self.start_button, alignment=Qt.AlignmentFlag.AlignCenter)
        footer.addWidget(self.info_label)
        footer.addStretch()
        footer.addWidget(self.version_label)

        main_layout.addWidget(header_widget)
        main_layout.addSpacing(10)
        main_layout.addLayout(time_layout)
        main_layout.addSpacing(20)
        main_layout.addLayout(footer)

        self._update_time_label()

    def _setup_video_ui(self) -> None:
        video_layout = QVBoxLayout(self.video_widget)
        video_layout.setContentsMargins(20, 20, 20, 20)
        video_layout.setSpacing(20)

        self.video_label = QLabel()
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_label.setStyleSheet("background-color: transparent;")
        self.video_label.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )

        button_layout = QHBoxLayout()

        self.pause_button = QPushButton()
        self.pause_button.setFixedSize(100, 100)
        self.pause_button.setStyleSheet(
            """
            QPushButton {
                background-color: #d9d9d9;
                color: black;
                border-radius: 50px;
                font-size: 16px;
            }
            """
        )
        self.pause_button.clicked.connect(self.toggle_pause)

        self.stop_button = QPushButton()
        self.stop_button.setFixedSize(100, 100)
        self.stop_button.setStyleSheet(
            """
            QPushButton {
                background-color: #ff0000;
                color: white;
                border-radius: 50px;
                font-size: 16px;
            }
            """
        )
        self.stop_button.clicked.connect(self.stop_video_manual)

        button_layout.addStretch()
        button_layout.addWidget(self.pause_button)
        button_layout.addSpacing(50)
        button_layout.addWidget(self.stop_button)
        button_layout.addStretch()

        video_layout.addWidget(self.video_label)
        video_layout.addLayout(button_layout)

    def _load_time_from_config(self) -> None:
        seconds = load_config()["user_settings"].get("work_time_seconds", 0)
        try:
            seconds = max(0, int(seconds))
        except (TypeError, ValueError):
            seconds = 0

        self.h, remainder = divmod(seconds, 3600)
        self.m, self.s = divmod(remainder, 60)

    def _save_time_to_config(self) -> None:
        update_config("user_settings", work_time_seconds=self._total_seconds())

    def _get_monitor_settings(self) -> tuple[str, bool, bool]:
        config = load_config()
        user_settings = config["user_settings"]
        monitoring_settings = config["monitoring_settings"]
        return (
            str(user_settings.get("selected_file") or ""),
            bool(monitoring_settings.get("gaze_enabled", False)),
            bool(monitoring_settings.get("glasses_enabled", False)),
        )

    def _create_arrow(self, text: str, callback) -> QPushButton:  # type: ignore[no-untyped-def]
        button = QPushButton(text)
        button.setObjectName("arrow_btn")
        button.clicked.connect(callback)
        return button

    def _total_seconds(self) -> int:
        return self.h * 3600 + self.m * 60 + self.s

    def _update_time_label(self) -> None:
        self.time_label.setText(f"{self.h:02}:{self.m:02}:{self.s:02}")

    def inc_h(self) -> None:
        self.h = (self.h + 1) % 24
        self._update_time_label()

    def inc_m(self) -> None:
        self.m = (self.m + 1) % 60
        self._update_time_label()

    def inc_s(self) -> None:
        self.s = (self.s + 1) % 60
        self._update_time_label()

    def dec_h(self) -> None:
        self.h = (self.h - 1) % 24
        self._update_time_label()

    def dec_m(self) -> None:
        self.m = (self.m - 1) % 60
        self._update_time_label()

    def dec_s(self) -> None:
        self.s = (self.s - 1) % 60
        self._update_time_label()

    def start_clicked(self) -> None:
        file_path, _, _ = self._get_monitor_settings()
        errors: list[str] = []

        camera = cv2.VideoCapture(0)
        if not camera.isOpened():
            errors.append(self.tr("Не удалось получить доступ к камере"))
        else:
            camera.release()

        if not file_path or not Path(file_path).is_file():
            errors.append(self.tr("Не выбран файл"))

        if self._total_seconds() == 0:
            errors.append(self.tr("Выберите время больше нуля"))

        if errors:
            WinDialog(self, "\n".join(errors), title=self.tr("Ошибка"))
            return

        self._save_time_to_config()
        self._animate_and_start()

    def _animate_and_start(self) -> None:
        self.animation = QPropertyAnimation(self.timer_widget, b"geometry")
        self.animation.setDuration(500)

        start_rect = self.timer_widget.geometry()
        end_rect = QRect(
            start_rect.x(),
            start_rect.y() + self.height(),
            start_rect.width(),
            start_rect.height(),
        )

        self.animation.setStartValue(start_rect)
        self.animation.setEndValue(end_rect)
        self.animation.finished.connect(self._start_video_process)
        self.animation.start()

    def _start_video_process(self) -> None:
        self.timer_widget.hide()
        self.video_widget.show()

        file_path, gaze, glasses = self._get_monitor_settings()
        self.thread = VideoThread(file_path, gaze, glasses, self._total_seconds())
        self.thread.change_pixmap_signal.connect(self.update_video_image)
        self.thread.finished_signal.connect(self.on_video_finished)
        self.thread.start()

        if self.on_start_callback:
            self.on_start_callback()

    @pyqtSlot(np.ndarray)
    def update_video_image(self, cv_img: np.ndarray) -> None:
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        height, width, channels = rgb_image.shape
        qt_image = QImage(
            rgb_image.data,
            width,
            height,
            channels * width,
            QImage.Format.Format_RGB888,
        )
        pixmap = QPixmap.fromImage(qt_image).scaled(
            self.video_label.width(),
            self.video_label.height(),
            Qt.AspectRatioMode.KeepAspectRatio,
        )
        self.video_label.setPixmap(pixmap)

    def toggle_pause(self) -> None:
        if self.thread is None:
            return

        self.thread.toggle_pause()
        self.pause_button.setText(
            self.tr("Продолжить") if self.thread.is_paused else self.tr("Пауза")
        )

    def stop_video_manual(self) -> None:
        if self.thread is not None:
            self.thread.stop()

    def on_video_finished(self) -> None:
        self.video_widget.hide()
        self.timer_widget.show()
        self.video_label.clear()
        self.thread = None
        self.pause_button.setText(self.tr("Пауза"))

        self.animation = QPropertyAnimation(self.timer_widget, b"geometry")
        self.animation.setDuration(500)
        self.animation.setStartValue(QRect(0, self.height(), self.width(), self.height()))
        self.animation.setEndValue(QRect(0, 0, self.width(), self.height()))
        self.animation.start()

    def retranslate_ui(self) -> None:
        self.start_button.setText(self.tr("СТАРТ"))
        self.info_label.setText(self.tr("Перед началом выберите файл"))
        self.version_label.setText(
            self.tr("Версия: 1.0.0").replace("1.0.0", __version__)
        )
        self.stop_button.setText(self.tr("Стоп"))
        self.pause_button.setText(self.tr("Пауза"))

    def changeEvent(self, event: QEvent) -> None:  # noqa: N802
        if event.type() == QEvent.Type.LanguageChange:
            self.retranslate_ui()
        super().changeEvent(event)

    def resizeEvent(self, event) -> None:  # type: ignore[no-untyped-def]
        self.timer_widget.resize(self.size())
        self.video_widget.resize(self.size())
        super().resizeEvent(event)
