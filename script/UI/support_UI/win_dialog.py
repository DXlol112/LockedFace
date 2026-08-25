from __future__ import annotations

import logging
from pathlib import Path

from PyQt6.QtCore import QRect, QSize, Qt, QUrl
from PyQt6.QtGui import QDesktopServices, QPaintEvent
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QStyle,
    QStyleOptionButton,
    QStylePainter,
    QVBoxLayout,
    QWidget,
)

logger = logging.getLogger(__name__)


class WrappingPushButton(QPushButton):
    """A push button whose text wraps and determines the button height."""

    _HORIZONTAL_PADDING = 32
    _VERTICAL_PADDING = 16
    _MINIMUM_WIDTH = 120

    def __init__(self, text: str, parent: QWidget | None = None) -> None:
        super().__init__(text, parent)
        self.setSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum
        )

    @staticmethod
    def _text_flags() -> int:
        return int(
            Qt.AlignmentFlag.AlignCenter
            | Qt.TextFlag.TextWordWrap
            | Qt.TextFlag.TextWrapAnywhere
        )

    def _text_height(self, width: int) -> int:
        text_width = max(1, width - self._HORIZONTAL_PADDING)
        bounds = self.fontMetrics().boundingRect(
            QRect(0, 0, text_width, 10_000), self._text_flags(), self.text()
        )
        return bounds.height()

    def hasHeightForWidth(self) -> bool:  # noqa: N802
        return True

    def heightForWidth(self, width: int) -> int:  # type: ignore # noqa: N802
        return max(
            self.fontMetrics().height() + self._VERTICAL_PADDING,
            self._text_height(width) + self._VERTICAL_PADDING,
        )

    def sizeHint(self) -> QSize:  # noqa: N802
        natural_width = (
            self.fontMetrics().horizontalAdvance(self.text())
            + self._HORIZONTAL_PADDING
        )
        maximum_width = self.maximumWidth()
        width = max(self._MINIMUM_WIDTH, min(natural_width, maximum_width))
        return QSize(width, self.heightForWidth(width))

    def minimumSizeHint(self) -> QSize:  # noqa: N802
        width = min(self._MINIMUM_WIDTH, self.maximumWidth())
        return QSize(width, self.heightForWidth(width))

    def paintEvent(self, event: QPaintEvent) -> None:  # type: ignore # noqa: N802
        del event
        option = QStyleOptionButton()
        self.initStyleOption(option)
        text = option.text
        option.text = ""

        painter = QStylePainter(self)
        painter.drawControl(QStyle.ControlElement.CE_PushButton, option)
        text_rect = self.style().subElementRect(QStyle.SubElement.SE_PushButtonContents, option, self) # pyright: ignore[reportOptionalMemberAccess]
        painter.setPen(option.palette.buttonText().color())
        painter.drawText(text_rect, self._text_flags(), text)


class WinDialog(QWidget):
    def __init__(
        self,
        parent: QWidget,
        message: str,
        _open_button: bool = False,
        text_open_button: str | None = None,
        title: str | None = None,
        button_url: str = "https://github.com/DXlol112/LockedFace/releases/latest",
    ) -> None:
        super().__init__(parent)
        self.setObjectName("overlay")
        self.setGeometry(parent.rect())
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Widget)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self._button_url = QUrl(button_url)

        self.dialog = QWidget(self)
        self.dialog.setObjectName("modalDialog")
        dialog_width = min(400, max(280, parent.width() - 40))
        self.dialog.setFixedWidth(dialog_width)
        self.dialog.setMinimumHeight(200)

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
        layout.addWidget(self.message_label, stretch=1)

        self.open_button: WrappingPushButton | None = None
        if _open_button:
            button_layout = QHBoxLayout()
            button_layout.addStretch()

            self.open_button = WrappingPushButton(
                text_open_button or self.tr("Открыть"), self.dialog
            )
            self.open_button.setObjectName("openButton")
            self.open_button.setMaximumWidth(max(120, dialog_width - 40))
            self.open_button.clicked.connect(self._open_url)
            button_layout.addWidget(self.open_button)

            button_layout.addStretch()
            layout.addLayout(button_layout)

        self._load_stylesheet()
        layout.activate()
        self.dialog.adjustSize()

        self._center_dialog()
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

    def _open_url(self) -> None:
        if self._button_url.isValid():
            QDesktopServices.openUrl(self._button_url)
