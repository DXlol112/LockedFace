from __future__ import annotations

import logging

from packaging.version import Version

from PyQt6.QtCore import QEvent, QSize, Qt, QUrl
from PyQt6.QtGui import QDesktopServices, QIcon, QPixmap
from PyQt6.QtWidgets import (
    QApplication,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from script.core import (
    __version__,
    get_application_dir,
    get_latest_version,
)
from script.core.i18n import set_application_language
from script.style.animations import RotateIconAnimation

from script.UI.support_UI import (
    WinDialog,
    add_action,
    add_advanced_settings,
    add_input_box,
    add_mini_dropdown_menu,
    add_toggle,
    create_separator,
)


logger = logging.getLogger(__name__)


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
        self.update_label = add_action(
            actions_layout,
            "static/btn_icon/refresh_btn.png",
            (51, 49),
            self.update_checker,
        )
        self.open_folder_label = add_action(
            actions_layout,
            "static/btn_icon/link_btn.png",
            (56, 46),
            self.open_folder,
        )
        self.source_code_label = add_action(
            actions_layout,
            "static/btn_icon/link_btn.png",
            (56, 46),
            self.open_github,
        )

        line = create_separator()

        toggle_layout = QVBoxLayout()
        toggle_layout.setContentsMargins(10, 0, 5, 0)
        toggle_layout.setSpacing(10)
        self.translations_label, self.translations_select = (
            add_mini_dropdown_menu(
                toggle_layout,
                values=("RU", "EN"),
                icon_path="static/btn_icon/angle-small-down.png",
                icon_size=(20, 20),
                config_key="translations_select",
            )
        )
        self.translations_select.currentTextChanged.connect(self._change_language)

        self.gaze_label, self.gaze_toggle = add_toggle(
            toggle_layout, "gaze_enabled"
        )
        toggle_layout.addSpacing(12)
        self.glasses_label, self.glasses_toggle = add_toggle(
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
        ) = add_advanced_settings(
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

    def _change_language(self, language: str) -> None:
        app = QApplication.instance()
        if app is not None:
            set_application_language(app, language) # pyright: ignore[reportArgumentType]

    def update_checker(self) -> None:
        try:
            last_version = get_latest_version()

            current = Version(__version__.removeprefix("v"))
            latest = Version(last_version.removeprefix("v"))

            if latest > current:
                WinDialog(
                    self,
                    message=self.tr(
                        "Доступна новая версия: {latest}\n"
                        "Установленная версия: {current}"
                    ).format(latest=last_version, current=__version__),
                    _open_button=True,
                    text_open_button=self.tr("Открыть страницу обновления"),
                    title=self.tr("Обновление"),
                )
                return

            WinDialog(
                self,
                message=self.tr(
                    "У вас установлена последняя версия ({version})."
                ).format(version=__version__),
                title=self.tr("Обновление"),
            )
        except Exception as error:
            logger.exception("Could not check for updates")
            WinDialog(
                self,
                message=self.tr("Не удалось проверить обновления: {error}").format(
                    error=str(error) or type(error).__name__
                ),
                title=self.tr("Ошибка"),
            )

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
        self.translations_label.setText(self.tr("Перевод"))
        self.gaze_label.setText(self.tr("Включить отслеживание глаз"))
        self.glasses_label.setText(self.tr("Наличие очков"))
        self._set_advanced_settings_text(self.tr("Дополнительные настройки"),
            self.tr("Здесь появятся дополнительные настройки."),
        )

    def changeEvent(self, event: QEvent) -> None:  # pyright: ignore[reportIncompatibleMethodOverride] # noqa: N802
        if event.type() == QEvent.Type.LanguageChange:
            self.retranslate_ui()
        super().changeEvent(event)
