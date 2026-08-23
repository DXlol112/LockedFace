from __future__ import annotations

from PyQt6.QtCore import QObject, QSize, Qt, QVariantAnimation
from PyQt6.QtGui import QIcon, QPixmap, QTransform
from PyQt6.QtWidgets import QAbstractButton


class RotateIconAnimation(QObject):
    """Animate an icon rotation on a button."""

    def __init__(
        self,
        button: QAbstractButton,
        icon_path: str,
        icon_size: QSize,
        duration: int = 180,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent or button)
        self._button = button
        self._icon = QPixmap(icon_path)
        self._icon_size = QSize(icon_size)
        self._angle = 0.0

        self._animation = QVariantAnimation(self)
        self._animation.setDuration(duration)
        self._animation.valueChanged.connect(self._set_angle)

    def rotate_to(self, target_angle: float) -> None:
        self._animation.stop()
        self._animation.setStartValue(self._angle)
        self._animation.setEndValue(target_angle)
        self._animation.start()

    def _set_angle(self, angle: float) -> None:
        self._angle = float(angle)
        if self._icon.isNull():
            return

        rotated_icon = self._icon.transformed(
            QTransform().rotate(self._angle),
            Qt.TransformationMode.SmoothTransformation,
        )
        self._button.setIcon(QIcon(rotated_icon))
        self._button.setIconSize(self._icon_size)
