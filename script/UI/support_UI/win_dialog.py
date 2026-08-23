from __future__ import annotations

import logging
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget


logger = logging.getLogger(__name__)


class WinDialog(QWidget):
    def __init__(self, parent: QWidget, message: str, title: str | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("overlay")
        self.setGeometry(parent.rect())
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Widget)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)

        self.dialog = QWidget(self)
        self.dialog.setObjectName("modalDialog")
        self.dialog.setFixedSize(400, 200)

        title_layout = QHBoxLayout()
        self.title_label = QLabel(title or self.tr("Сообщение"))
        self.title_label.setObjectName("titleLabel")
        title_layout.addWidget(self.title_label)
        title_layout.addStretch()

        self.close_button = QPushButton("×")
        self.close_button.setObjectName("closeButton")
        self.close_button.setFixedSize(30, 30)
        self.close_button.clicked.connect(self._close)
        title_layout.addWidget(self.close_button)

        self.message_label = QLabel(message)
        self.message_label.setObjectName("messageLabel")
        self.message_label.setWordWrap(True)
        self.message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.message_label.setTextFormat(Qt.TextFormat.PlainText)

        layout = QVBoxLayout(self.dialog)
        layout.addLayout(title_layout)
        layout.addWidget(self.message_label)
        layout.addSpacing(20)

        self._center_dialog()
        self._load_stylesheet()
        self.raise_()
        self.show()

    def _center_dialog(self) -> None:
        parent_rect = self.parentWidget().rect()  # type: ignore[union-attr]
        self.dialog.move(
            (parent_rect.width() - self.dialog.width()) // 2,
            (parent_rect.height() - self.dialog.height()) // 2,
        )

    def _load_stylesheet(self) -> None:
        style_path = Path("script/style/dialog_win.qss")
        try:
            self.setStyleSheet(style_path.read_text(encoding="utf-8"))
        except OSError as error:
            logger.warning("Could not load dialog stylesheet %s: %s", style_path, error)

    def mousePressEvent(self, event) -> None:  # type: ignore[no-untyped-def]
        if not self.dialog.geometry().contains(event.position().toPoint()):
            self._close()
        super().mousePressEvent(event)

    def _close(self) -> None:
        self.hide()
        self.deleteLater()
