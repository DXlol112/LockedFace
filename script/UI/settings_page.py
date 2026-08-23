from __future__ import annotations

from PyQt6.QtCore import QEvent, QSize, Qt, QUrl
from PyQt6.QtGui import QDesktopServices, QIcon, QPixmap
from PyQt6.QtWidgets import (
    QCheckBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from script.core import __version__, get_application_dir, load_config, update_config
from script.style.animations import RotateIconAnimation


class SettingsPage(QWidget):
    def __init__(self, on_back) -> None:  # type: ignore[no-untyped-def]
        super().__init__()
        self.on_back = on_back
        self._advanced_expanded = False

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        header_widget = QWidget()
        header_widget.setObjectName("header_sett")
        header_widget.setFixedHeight(60)
        header = QHBoxLayout(header_widget)

        self.back_button = QPushButton()
        self.back_button.setObjectName("back_btn")
        self.back_button.setIcon(QIcon("static/btn_icon/back_btn.png"))
        self.back_button.setIconSize(QSize(71, 48))
        self.back_button.clicked.connect(self.on_back)
        header.addWidget(self.back_button)
        header.addStretch()
        main_layout.addWidget(header_widget)

        self.scroll_area = QScrollArea()
        self.scroll_area.setObjectName("settings_scroll")
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)

        content = QWidget()
        content.setObjectName("settings_content")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 3, 0, 20)
        content_layout.setSpacing(0)
        self.scroll_area.setWidget(content)
        main_layout.addWidget(self.scroll_area)

        info_block = QGridLayout()
        info_block.setContentsMargins(0, 0, 0, 0)
        info_block.setSpacing(0)

        icon = QLabel()
        icon.setPixmap(QPixmap("static/icon/logo_icon.svg"))
        icon.setObjectName("icon_project")
        icon.setFixedSize(218, 218)
        icon.setScaledContents(True)

        text_block = QVBoxLayout()
        text_block.setSpacing(10)
        self.name_label = QLabel("LockedFace")
        self.name_label.setObjectName("name_set")
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.version_label = QLabel()
        self.version_label.setObjectName("ver_set")
        self.version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        text_block.addWidget(self.name_label)
        text_block.addWidget(self.version_label)

        info_block.addWidget(
            icon, 0, 0, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        )
        info_block.addLayout(text_block, 0, 1, Qt.AlignmentFlag.AlignCenter)
        right_spacer = QWidget()
        right_spacer.setFixedWidth(218)
        info_block.addWidget(right_spacer, 0, 2)
        info_block.setColumnStretch(1, 1)

        actions_layout = QVBoxLayout()
        actions_layout.setSpacing(10)
        actions_layout.setContentsMargins(10, 0, 0, 0)
        self.update_label = self._add_action(
            actions_layout,
            "static/btn_icon/refresh_btn.png",
            (51, 49),
            self.update_checker,
        )
        self.open_folder_label = self._add_action(
            actions_layout,
            "static/btn_icon/link_btn.png",
            (56, 46),
            self.open_folder,
        )
        self.source_code_label = self._add_action(
            actions_layout,
            "static/btn_icon/link_btn.png",
            (56, 46),
            self.open_github,
        )

        line = self._create_separator()

        toggle_layout = QVBoxLayout()
        toggle_layout.setContentsMargins(10, 0, 5, 0)
        toggle_layout.setSpacing(10)
        self.gaze_label, self.gaze_toggle = self._add_toggle(
            toggle_layout, "gaze_enabled"
        )
        toggle_layout.addSpacing(12)
        self.glasses_label, self.glasses_toggle = self._add_toggle(
            toggle_layout, "glasses_enabled"
        )

        content_layout.addLayout(info_block)
        content_layout.addSpacing(20)
        content_layout.addLayout(actions_layout)
        content_layout.addSpacing(20)
        content_layout.addWidget(line)
        content_layout.addSpacing(10)
        content_layout.addLayout(toggle_layout)
        content_layout.addSpacing(20)

        (
            self.advanced_settings_label,
            self.advanced_settings_button,
            self.advanced_content,
            self.advanced_placeholder_label,
        ) = self._add_advanced_settings(
            content_layout,
            "static/btn_icon/angle-small-down.png",
            (40, 40),
            self.advanced_settings_open,
        )
        self._advanced_icon_animation = RotateIconAnimation(
            self.advanced_settings_button,
            "static/btn_icon/angle-small-down.png",
            QSize(40, 40),
            parent=self,
        )

        self.advanced_content.hide()
        content_layout.addStretch()

        self.retranslate_ui()

    def _add_action(
        self,
        layout: QVBoxLayout,
        icon_path: str,
        icon_size: tuple[int, int],
        callback,
    ) -> QLabel:  # type: ignore[no-untyped-def]
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

    def _add_toggle(
        self, layout: QVBoxLayout, config_key: str
    ) -> tuple[QLabel, QCheckBox]:
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

    def _add_advanced_settings(
        self,
        layout: QVBoxLayout,
        icon_path: str,
        icon_size: tuple[int, int],
        callback,
    ) -> tuple[QLabel, QPushButton, QFrame, QLabel]:  # type: ignore[no-untyped-def]
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

    def _create_separator(self) -> QFrame:
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        line.setObjectName("line_sep")
        line.setFixedHeight(1)
        return line

    def update_checker(self) -> None:
        return None

    def open_folder(self) -> None:
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(get_application_dir())))

    def open_github(self) -> None:
        QDesktopServices.openUrl(QUrl("https://github.com/DXlol112/LockedFace"))

    def advanced_settings_open(self) -> None:
        self._advanced_expanded = not self._advanced_expanded
        self.advanced_content.setVisible(self._advanced_expanded)
        self._advanced_icon_animation.rotate_to(
            90.0 if self._advanced_expanded else 0.0
        )

    def _set_advanced_settings_text(self, title: str, content: str) -> None:
        self.advanced_settings_label.setText(title)
        self.advanced_placeholder_label.setText(content)

    def retranslate_ui(self) -> None:
        self.version_label.setText(
            self.tr("Версия: 1.0.0").replace("1.0.0", __version__)
        )
        self.update_label.setText(self.tr("Проверить обновления"))
        self.open_folder_label.setText(self.tr("Открыть папку приложения"))
        self.source_code_label.setText(self.tr("Исходный код"))
        self.gaze_label.setText(self.tr("Включить отслеживание глаз"))
        self.glasses_label.setText(self.tr("Наличие очков"))
        self._set_advanced_settings_text(self.tr("Дополнительные настройки"),
            self.tr("Здесь появятся дополнительные настройки."),
        )

    def changeEvent(self, event: QEvent) -> None:  # pyright: ignore[reportIncompatibleMethodOverride] # noqa: N802
        if event.type() == QEvent.Type.LanguageChange:
            self.retranslate_ui()
        super().changeEvent(event)
