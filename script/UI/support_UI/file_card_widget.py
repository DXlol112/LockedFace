import os
import random
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel, QStackedWidget
from PyQt6.QtCore import Qt, QUrl, QTimer
from PyQt6.QtGui import QPixmap, QMovie
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput, QVideoSink
from PyQt6.QtMultimediaWidgets import QVideoWidget



class FileCard(QFrame):
    def __init__(self, path, on_click):
        super().__init__()
        
        self.path = path
        self.on_click = on_click
        self.setFixedSize(150,180)
        self.setObjectName("file_card")

        layout = QVBoxLayout(self)
        self.stack = QStackedWidget()
        self.stack.setFixedSize(130,130)

        self.preview_label = QLabel()
        self.preview_label.setScaledContents(True)

        self.video_widget = QVideoWidget()
        self.media_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.media_player.setAudioOutput(self.audio_output)
        self.audio_output.setMuted(True)
        self.media_player.setVideoOutput(self.video_widget)

        self.media_player.mediaStatusChanged.connect(self._handle_media_status)

        self.sink = QVideoSink()
        self.media_player.setVideoSink(self.sink)

        self.stack.addWidget(self.preview_label)
        self.stack.addWidget(self.video_widget)

        self.movie = None
        self.setup_preview()

        self.name = QLabel(os.path.basename(path))
        self.name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.name.setStyleSheet("border: none;")

        layout.addWidget(self.stack)
        layout.addWidget(self.name)

        self.stop_timer = QTimer()
        self.stop_timer.setSingleShot(True)
        self.stop_timer.timeout.connect(self.stop_media)

    def setup_preview(self):
        ext = self.path.lower()
        if ext.endswith(('.png', '.jpg', '.jpeg', 'webp')):
            self.preview_label.setPixmap(QPixmap(self.path))
        elif ext.endswith('.gif'):
            self.movie = QMovie(self.path)
            self.movie.setScaledSize(self.stack.size())
            self.preview_label.setMovie(self.movie)
            self.movie.start()
            self.movie.setPaused(True)
        elif ext.endswith('.mp4'):
            self.preview_label.setText("Загрузка...")
            self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.sink.videoFrameChanged.connect(self._on_video_frame_changed)
            self.media_player.durationChanged.connect(self._seek_to_random_for_preview)

            self.media_player.setSource(QUrl.fromLocalFile(self.path))
            self.media_player.play()

    def _handle_media_status(self, status):
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            self.media_player.setPosition(0)
            self.media_player.play()
    
    def _seek_to_random_for_preview(self, duration):
        if duration > 0:
            random_ms = random.randint(0, max(0, duration - 1000))
            self.media_player.setPosition(random_ms)
            try:
                self.media_player.durationChanged.disconnect(self._seek_to_random_for_preview)
            except: pass
            
    def _on_video_frame_changed(self, frame):
        image = frame.toImage()
        if not image.isNull():
            pixmap = QPixmap.fromImage(image)
            self.preview_label.setPixmap(pixmap.scaled(self.stack.size(), 
                                        Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                                        Qt.TransformationMode.SmoothTransformation
            ))
        try:
            self.sink.videoFrameChanged.disconnect(self._on_video_frame_changed)
        except: pass
        self.media_player.setPosition(0)

    def enterEvent(self, event):
        ext = self.path.lower()
        if ext.endswith('.gif') and self.movie:
            self.movie.setPaused(False)
        elif ext.endswith('.mp4'):
            self.stack.setCurrentWidget(self.video_widget)
            self.media_player.setPosition(0)
            self.media_player.play()
            self.stop_timer.start(5000)
        super().enterEvent(event)
    
    def leaveEvent(self, event): # pyright: ignore[reportIncompatibleMethodOverride]
        self.stop_media()
        super().leaveEvent(event)
    
    def stop_media(self):
        ext = self.path.lower()
        if ext.endswith('.gif') and self.movie:
            self.movie.setPaused(True)
        elif ext.endswith('.mp4'):
            self.media_player.stop()
            self.stack.setCurrentWidget(self.preview_label)

    def mousePressEvent(self, event): # pyright: ignore[reportIncompatibleMethodOverride]
        if event.button() == Qt.MouseButton.LeftButton:
            self.on_click(self.path)
    
    def set_selected(self, is_selected):
        if is_selected:
            self.setStyleSheet("QFrame#file_card { border: 3px solid green; border-radius: 10px; }")
        else:
            self.setStyleSheet("QFrame#file_card { border: 1px solid gray; border-radius: 10px; }")