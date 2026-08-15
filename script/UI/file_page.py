from __future__ import annotations

import shutil
from pathlib import Path

from PyQt6.QtCore import QEvent, QSize, Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QFileDialog,
    QGridLayout,
    QHBoxLayout,
    QScrollArea,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from script.UI.support_UI import FileCard, WinDialog
from script.core import get_media_dir, load_config, update_config


class FilePage(QWidget):
    def __init__(self, on_back) -> None:  # type: ignore[no-untyped-def]
        super().__init__()
        self.confirm_delete = False
        self.on_back = on_back
        self.selected_path = self._load_selection()
        self.cards: list[FileCard] = []

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

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setObjectName("file_scroll")
        container = QWidget()
        self.grid = QGridLayout(container)
        self.grid.setSpacing(15)
        self.scroll_area.setWidget(container)

        footer = QWidget()
        footer_layout = QVBoxLayout(footer)
        footer_layout.setContentsMargins(0, 0, 0, 20)
        footer_layout.setSpacing(10)
        footer_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.add_file_button = QPushButton()
        self.add_file_button.setObjectName("add_file_btn")
        self.add_file_button.setFixedSize(QSize(300, 45))
        self.add_file_button.clicked.connect(self.open_system_dialog)

        self.delete_button = QPushButton()
        self.delete_button.setObjectName("add_del_btn")
        self.delete_button.setFixedSize(QSize(300, 45))
        self.delete_button.clicked.connect(self.delete_file)

        footer_layout.addWidget(self.add_file_button)
        footer_layout.addWidget(self.delete_button)

        main_layout.addWidget(header_widget)
        main_layout.addSpacing(10)
        main_layout.addWidget(self.scroll_area)
        main_layout.setStretchFactor(self.scroll_area, 1)
        main_layout.addSpacing(15)
        main_layout.addWidget(footer)

        self.retranslate_ui()
        self.refresh_gallery()

    def _load_selection(self) -> str | None:
        selected_file = load_config().get("selected_file")
        if not selected_file:
            return None

        path = Path(str(selected_file)).resolve()
        return str(path) if self._is_managed_media(path) and path.is_file() else None

    def _is_managed_media(self, path: Path) -> bool:
        try:
            path.resolve().relative_to(get_media_dir().resolve())
        except ValueError:
            return False
        return True

    def _destination_for(self, source: Path) -> Path:
        media_dir = get_media_dir()
        candidate = media_dir / source.name
        counter = 1
        while candidate.exists():
            candidate = media_dir / f"{source.stem} ({counter}){source.suffix}"
            counter += 1
        return candidate

    def open_system_dialog(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            self.tr("Выбрать файл"),
            "",
            self.tr("Медиафайлы (*.png *.jpg *.jpeg *.webp *.mp4 *.gif)"),
        )
        if not file_path:
            return

        source = Path(file_path)
        destination = self._destination_for(source)
        try:
            shutil.copy2(source, destination)
        except OSError as error:
            WinDialog(
                self,
                self.tr("Не удалось добавить файл: {error}").format(error=error),
                title=self.tr("Ошибка"),
            )
            return

        self.refresh_gallery()
        self.select_file(destination)

    def refresh_gallery(self) -> None:
        while self.grid.count():
            item = self.grid.takeAt(0)
            if widget := item.widget():
                widget.deleteLater()

        self.cards.clear()
        files = sorted(
            (path for path in get_media_dir().iterdir() if path.is_file()),
            key=lambda path: path.name.lower(),
        )

        for index, path in enumerate(files):
            card = FileCard(str(path), self.select_file)
            card.set_selected(str(path) == self.selected_path)
            self.cards.append(card)
            self.grid.addWidget(card, index // 4, index % 4)

    def select_file(self, path: str | Path) -> None:
        if self.confirm_delete:
            self.reset_delete_button()

        selected = Path(path).resolve()
        if not self._is_managed_media(selected):
            return

        self.selected_path = str(selected)
        for card in self.cards:
            card.set_selected(card.path == self.selected_path)
        update_config(selected_file=self.selected_path)

    def delete_file(self) -> None:
        if self.selected_path is None:
            return

        if not self.confirm_delete:
            self.confirm_delete = True
            self.delete_button.setText(self.tr("Вы уверены?"))
            self.delete_button.setStyleSheet(
                "background-color: #ff4d4d; color: white; font-weight: bold;"
            )
            for card in self.cards:
                if card.path == self.selected_path:
                    card.setStyleSheet(
                        "QFrame#file_card { border: 3px solid red; border-radius: 10px; }"
                    )
            return

        path_to_remove = Path(self.selected_path)
        if not self._is_managed_media(path_to_remove):
            self.reset_delete_button()
            return

        try:
            for card in self.cards:
                if card.path == self.selected_path:
                    card.cleanup_resources()
                    break
            path_to_remove.unlink(missing_ok=True)
        except OSError as error:
            WinDialog(
                self,
                self.tr("Не удалось удалить файл: {error}").format(error=error),
                title=self.tr("Ошибка"),
            )
            self.reset_delete_button()
            return

        self.selected_path = None
        update_config(selected_file=None)
        self.reset_delete_button()
        self.refresh_gallery()

    def reset_delete_button(self) -> None:
        self.confirm_delete = False
        self.delete_button.setText(self.tr("Удалить выбранный файл"))
        self.delete_button.setStyleSheet("")

    def retranslate_ui(self) -> None:
        self.add_file_button.setText(self.tr("Добавить файл"))
        self.reset_delete_button()

    def changeEvent(self, event: QEvent) -> None:  # noqa: N802
        if event.type() == QEvent.Type.LanguageChange:
            self.retranslate_ui()
        super().changeEvent(event)
