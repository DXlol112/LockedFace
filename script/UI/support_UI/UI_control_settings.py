"""Factories for controls used on the settings page."""

from __future__ import annotations

from collections.abc import Callable, Sequence

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)

from script.core import load_config, update_config


class _MiniDropdown(QComboBox):
    """A compact combo box with its value painted above the native control."""

    def __init__(self, icon_path: str, icon_size: tuple[int, int]) -> None:
        super().__init__()
        self._icon_size = QSize(*icon_size)

        self._icon_label = QLabel(self)
        self._icon_label.setObjectName("mini_dropdown_icon")
        self._icon_label.setAttribute(
            Qt.WidgetAttribute.WA_TransparentForMouseEvents, True
        )
        self._icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._icon_label.setPixmap(QIcon(icon_path).pixmap(self._icon_size))

        self._value_label = QLabel(self)
        self._value_label.setObjectName("mini_dropdown_value")
        self._value_label.setAttribute(
            Qt.WidgetAttribute.WA_TransparentForMouseEvents, True
        )
        self._value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.currentTextChanged.connect(self._show_selected_value)

    def _show_selected_value(self, value: str) -> None:
        self._value_label.setText(value)
        self._raise_overlays()

    def _raise_overlays(self) -> None:
        self._icon_label.raise_()
        self._value_label.raise_()

    def resizeEvent(self, event) -> None:  # type: ignore[no-untyped-def] # noqa: N802
        super().resizeEvent(event)
        icon_width = self._icon_size.width()
        icon_height = self._icon_size.height()
        self._icon_label.setGeometry(
            self.width() - icon_width,
            (self.height() - icon_height) // 2,
            icon_width,
            icon_height,
        )
        self._value_label.setGeometry(0, 0, self.width() - icon_width, self.height())
        self._raise_overlays()

    def showPopup(self) -> None:  # noqa: N802
        super().showPopup()
        popup = self.view().window() # type: ignore
        popup.setFixedWidth(self.width()) # type: ignore
        self.view().setFixedWidth(self.width()) # pyright: ignore[reportOptionalMemberAccess]
        popup.raise_() # type: ignore
        self._raise_overlays()


def add_action(
    layout: QVBoxLayout,
    icon_path: str,
    icon_size: tuple[int, int],
    callback: Callable[[], None],
) -> QLabel:
    """Add an action row with a label and an icon button."""
    row = QHBoxLayout()
    label = QLabel()
    label.setObjectName("text_settings")
    button = QPushButton()
    button.setObjectName("settings_btn")
    button.setIcon(QIcon(icon_path))
    button.setIconSize(QSize(*icon_size))
    button.clicked.connect(callback)
    row.addWidget(label)
    row.addStretch()
    row.addWidget(button)
    layout.addLayout(row)
    return label


def add_input_box(
    layout: QVBoxLayout,
    value_range: tuple[float, float],
    config_key: str,
) -> tuple[QLabel, QDoubleSpinBox]:
    """Add a numeric input and persist changes under ``config_key``."""
    row = QHBoxLayout()

    label = QLabel()
    label.setObjectName("text_settings")

    input_box = QDoubleSpinBox()
    input_box.setRange(*value_range)
    input_box.setDecimals(2)
    input_box.setSingleStep(0.01)
    input_box.setObjectName("input_box")
    input_box.setValue(float(load_config().get(config_key, 4)))
    input_box.valueChanged.connect(
        lambda number: update_config(**{config_key: number})
    )

    row.addWidget(label)
    row.addStretch()
    row.addWidget(input_box)
    layout.addLayout(row)

    return label, input_box


def add_toggle(
    layout: QVBoxLayout, config_key: str
) -> tuple[QLabel, QCheckBox]:
    """Add a checkbox and persist its checked state."""
    row = QHBoxLayout()
    label = QLabel()
    label.setObjectName("text_settings")
    toggle = QCheckBox()
    toggle.setObjectName("toggle_btn")
    toggle.setChecked(bool(load_config().get(config_key, False)))
    toggle.toggled.connect(lambda checked: update_config(**{config_key: checked}))
    row.addWidget(label)
    row.addStretch()
    row.addWidget(toggle)
    layout.addLayout(row)
    return label, toggle


def add_advanced_settings(
    layout: QVBoxLayout,
    icon_path: str,
    icon_size: tuple[int, int],
    callback: Callable[[], None],
) -> tuple[QLabel, QPushButton, QFrame, QLabel]:
    """Add an expandable settings card and its content as one widget."""
    card = QFrame()
    card.setObjectName("advanced_settings_card")
    card_layout = QVBoxLayout(card)
    card_layout.setContentsMargins(0, 0, 0, 0)
    card_layout.setSpacing(10)

    header_layout = QHBoxLayout()
    header_layout.setContentsMargins(10, 0, 5, 0)
    header_layout.setSpacing(10)

    label = QLabel()
    label.setObjectName("advanced_settings_label")
    button = QPushButton()
    button.setObjectName("advanced_settings_button")
    button.setIcon(QIcon(icon_path))
    button.setIconSize(QSize(*icon_size))
    button.setFixedSize(48, 48)
    button.clicked.connect(callback)

    header_layout.addWidget(label)
    header_layout.addStretch()
    header_layout.addWidget(button)
    card_layout.addLayout(header_layout)

    content = QFrame()
    content.setObjectName("advanced_settings_content")
    content_layout = QVBoxLayout(content)
    content_layout.setContentsMargins(15, 0, 5, 0)
    content_layout.setSpacing(10)

    content_label = QLabel()
    content_label.setObjectName("advanced_settings_placeholder")
    content_label.setWordWrap(True)
    content_layout.addWidget(content_label)
    card_layout.addWidget(content)

    layout.addWidget(card)
    return label, button, content, content_label


def add_mini_dropdown_menu(
    layout: QVBoxLayout,
    values: Sequence[str],
    icon_path: str,
    icon_size: tuple[int, int],
    config_key: str,
) -> tuple[QLabel, QComboBox]:
    """Add a compact dropdown and persist its value under ``config_key``."""
    items = tuple(values)
    if not items:
        raise ValueError("Dropdown values cannot be empty")

    icon_width, icon_height = icon_size
    if icon_width <= 0 or icon_height <= 0:
        raise ValueError("Dropdown icon size must be positive")

    row = QHBoxLayout()
    label = QLabel()
    label.setObjectName("text_settings")

    dropdown = _MiniDropdown(icon_path, icon_size)
    dropdown.setObjectName("mini_dropdown")
    dropdown.addItems(items)
    dropdown.setFixedSize(50, 26)
    dropdown.view().setObjectName("mini_dropdown_list") # type: ignore
    dropdown.view().setFixedWidth(50) # type: ignore

    saved_value = str(load_config().get(config_key, items[0]))
    dropdown.setCurrentText(saved_value if saved_value in items else items[0])
    dropdown._show_selected_value(dropdown.currentText())
    dropdown.currentTextChanged.connect(
        lambda value: _save_dropdown_selection(config_key, value, items)
    )

    row.addWidget(label)
    row.addStretch()
    row.addWidget(dropdown)
    layout.addLayout(row)
    return label, dropdown


def _save_dropdown_selection(
    config_key: str,
    value: str,
    allowed_values: Sequence[str],
) -> None:
    """Persist a value emitted by a configured mini dropdown."""
    if value in allowed_values:
        update_config(**{config_key: value})


def create_separator() -> QFrame:
    """Create a horizontal separator for settings groups."""
    line = QFrame()
    line.setFrameShape(QFrame.Shape.HLine)
    line.setFrameShadow(QFrame.Shadow.Sunken)
    line.setObjectName("line_sep")
    line.setFixedHeight(1)
    return line


