from __future__ import annotations

import logging
import random
from pathlib import Path

from PyQt6.QtCore import QEvent, QTimer, Qt, QUrl
from PyQt6.QtGui import QMovie, QPixmap
from PyQt6.QtMultimedia import QAudioOutput, QMediaPlayer, QVideoSink
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtWidgets import QFrame, QLabel, QStackedWidget, QVBoxLayout


logger = logging.getLogger(__name__)


class FileCard(QFrame):
    def __init__(self, path: str, on_click) -> None:  # type: ignore[no-untyped-def]
        super().__init__()
        self.path = path
        self.on_click = on_click
        self.setFixedSize(150, 180)
        self.setObjectName("file_card")

        layout = QVBoxLayout(self)
        self.stack = QStackedWidget()
        self.stack.setFixedSize(130, 130)
        self.preview_label = QLabel()
        self.preview_label.setScaledContents(True)

        self.video_widget = QVideoWidget()
        self.media_player = QMediaPlayer(self)
        self.audio_output = QAudioOutput(self)
        self.audio_output.setMuted(True)
        self.media_player.setAudioOutput(self.audio_output)
        self.media_player.setVideoOutput(self.video_widget)
        self.sink = QVideoSink(self)
        self.media_player.mediaStatusChanged.connect(self._handle_media_status)

        self.stack.addWidget(self.preview_label)
        self.stack.addWidget(self.video_widget)

        self.movie: QMovie | None = None
        self.stop_timer = QTimer(self)
        self.stop_timer.setSingleShot(True)
        self.stop_timer.timeout.connect(self.stop_media)

        self.name_label = QLabel(Path(path).name)
        self.name_label.setObjectName("file_card_name")
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.stack)
        layout.addWidget(self.name_label)

        self.setup_preview()

    def setup_preview(self) -> None:
        suffix = Path(self.path).suffix.lower()
        if suffix in {".png", ".jpg", ".jpeg", ".webp"}:
            self.preview_label.setPixmap(QPixmap(self.path))
        elif suffix == ".gif":
            self.movie = QMovie(self.path)
            self.movie.setScaledSize(self.stack.size())
            self.preview_label.setMovie(self.movie)
            self.movie.start()
            self.movie.setPaused(True)
        elif suffix == ".mp4":
            self.preview_label.setText(self.tr("Загрузка…"))
            self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.media_player.setVideoSink(self.sink)
            self.sink.videoFrameChanged.connect(self._on_video_frame_changed)
            self.media_player.durationChanged.connect(self._seek_to_random_for_preview)
            self.media_player.setSource(QUrl.fromLocalFile(self.path))
            self.media_player.play()

    def _handle_media_status(self, status: QMediaPlayer.MediaStatus) -> None:
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            self.media_player.setPosition(0)
            self.media_player.play()

    def _seek_to_random_for_preview(self, duration: int) -> None:
        if duration <= 0:
            return

        self.media_player.setPosition(random.randint(0, max(0, duration - 1000)))
        try:
            self.media_player.durationChanged.disconnect(self._seek_to_random_for_preview)
        except TypeError:
            pass

    def _on_video_frame_changed(self, frame) -> None:  # type: ignore[no-untyped-def]
        image = frame.toImage()
        if not image.isNull():
            pixmap = QPixmap.fromImage(image).scaled(
                self.stack.size(),
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation,
            )
            self.preview_label.setPixmap(pixmap)
        try:
            self.sink.videoFrameChanged.disconnect(self._on_video_frame_changed)
        except TypeError:
            pass
        self.media_player.setPosition(0)
        self.media_player.stop()

    def enterEvent(self, event) -> None:  # type: ignore[no-untyped-def]
        suffix = Path(self.path).suffix.lower()
        if suffix == ".gif" and self.movie:
            self.movie.setPaused(False)
        elif suffix == ".mp4":
            self.stack.setCurrentWidget(self.video_widget)
            self.media_player.setVideoOutput(self.video_widget)
            self.media_player.setPosition(0)
            self.media_player.play()
            self.stop_timer.start(5000)
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:  # type: ignore[no-untyped-def]
        self.stop_media()
        super().leaveEvent(event)

    def stop_media(self) -> None:
        suffix = Path(self.path).suffix.lower()
        if suffix == ".gif" and self.movie:
            self.movie.setPaused(True)
        elif suffix == ".mp4":
            self.media_player.stop()
            self.stack.setCurrentWidget(self.preview_label)

    def mousePressEvent(self, event) -> None:  # type: ignore[no-untyped-def]
        if event.button() == Qt.MouseButton.LeftButton:
            self.on_click(self.path)

    def set_selected(self, is_selected: bool) -> None:
        self.setProperty("selected", is_selected)
        self._refresh_style()

    def set_delete_pending(self, is_pending: bool) -> None:
        self.setProperty("deletePending", is_pending)
        self._refresh_style()

    def _refresh_style(self) -> None:
        style = self.style()
        if style is not None:
            style.unpolish(self)
            style.polish(self)
        self.update()

    def cleanup_resources(self) -> None:
        try:
            self.stop_media()
            self.media_player.setSource(QUrl())
            if self.movie:
                self.movie.stop()
                self.movie = None
        except RuntimeError as error:
            logger.warning("Could not clean up media resources: %s", error)

    def changeEvent(self, event: QEvent) -> None:  # noqa: N802
        if event.type() == QEvent.Type.LanguageChange and self.preview_label.text():
            self.preview_label.setText(self.tr("Загрузка…"))
        super().changeEvent(event)
