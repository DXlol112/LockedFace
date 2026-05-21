from PyQt6.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, 
    QScrollArea, QGridLayout, QFrame, QFileDialog, QLayoutItem
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QPixmap

from script.UI.support_UI.file_card_widget import FileCard
from script.core import get_resource_path, get_config_path, get_base_dir

import json
from pathlib import Path
import os
import shutil


class FilePage(QWidget):
    def __init__(self, on_back):
        super().__init__()

        self.confirm_delete = False
        self.on_back = on_back

        self.json_path = str(get_config_path())
        self.selected_path = self.load_selection()
        self.cards = []


        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

    #----------------Header---------------------#
        header_widget = QWidget()
        header_widget.setObjectName("header_sett")
        header_widget.setFixedHeight(60)

        header = QHBoxLayout(header_widget)

        self.back_btn = QPushButton()
        self.back_btn.setObjectName("back_btn")
        self.back_btn.setIcon(QIcon(str(get_resource_path("static/btn_icon/back_btn.png"))))
        self.back_btn.setIconSize(QSize(71, 48))
        
        self.back_btn.clicked.connect(self.on_back)
        
        header.addWidget(self.back_btn)
        header.addStretch()
    #----------------------gallery-----------------#
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setObjectName("file_scroll")

        self.container = QWidget()
        self.grid = QGridLayout(self.container)
        self.grid.setSpacing(15)
        self.scroll_area.setWidget(self.container)

    #------------------------btn_footer--------------------#
        footer = QWidget()
        footer_layout = QVBoxLayout(footer)
        footer_layout.setContentsMargins(0,0,0,20)
        footer_layout.setSpacing(10)
        footer_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.add_file = QPushButton("Добавить файл")
        self.add_file.setObjectName("add_file_btn")
        self.add_file.setFixedSize(QSize(300,45))
        self.add_file.clicked.connect(self.open_system_dialog)

        self.add_del = QPushButton("Удалить выбранный файл")
        self.add_del.setObjectName("add_del_btn")
        self.add_del.setFixedSize(QSize(300,45))
        self.add_del.clicked.connect(self.delete_file)
            
        footer_layout.addWidget(self.add_file)
        footer_layout.addWidget(self.add_del)
    #----------------All-------------------------#
        main_layout.addWidget(header_widget)
        main_layout.addSpacing(10)
        main_layout.addWidget(self.scroll_area)
        main_layout.setStretchFactor(self.scroll_area, 1)
        main_layout.addSpacing(15)
        main_layout.addWidget(footer)

    #---------------------Functions---------------#
        self.refresh_gallery()

    def open_system_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Выбрать файл", "", "Images/Video (*.png *.jpg *.webp *.mp4 *.gif)")
        if file_path:
            media_dir = get_base_dir() / "media"
            media_dir.mkdir(exist_ok=True)
        
            dest_path = media_dir / os.path.basename(file_path)
            shutil.copy2(file_path, dest_path)

            self.refresh_gallery()
            self.select_file(str(dest_path))

   
    def refresh_gallery(self):
        while self.grid.count():
            item = self.grid.takeAt(0)
            if item.widget(): # pyright: ignore[reportOptionalMemberAccess]
                item.widget().deleteLater() # pyright: ignore[reportOptionalMemberAccess]
        
        self.cards.clear()

        media_dir = get_base_dir() / "media"
        media_dir.mkdir(exist_ok=True)

        files = list(media_dir.glob("*.*"))
        cols = 4

        for index, path in enumerate(files):
            str_path = str(path.as_posix())
            card = FileCard(str_path, self.select_file)

            if str_path == self.selected_path:
                card.set_selected(True)
            
            self.cards.append(card)
            self.grid.addWidget(card, index // cols, index % cols)
            
    
    def select_file(self, path):
        if self.confirm_delete:
           self.reset_delete_button()
        
        path = str(Path(path).as_posix())
        self.selected_path = path

        for card in self.cards:
            card.set_selected(card.path == path)

        self.save_selection(path)

        
    def load_selection(self):
        if os.path.exists(self.json_path):
            try:
                with open(self.json_path, "r", encoding="utf-8") as f:
                    return json.load(f).get("selected_file")
            except:
                return None
        return None
    
    def delete_file(self):
        if not self.selected_path:
            return

        if not self.confirm_delete:
            self.confirm_delete = True
            self.add_del.setText("Вы уверены ?")
            self.add_del.setStyleSheet("background-color: #ff4d4d; color: white; font-weight: bold;")

            for card in self.cards:
                if card.path == self.selected_path:
                    card.setStyleSheet("QFrame#file_card { border: 3px solid red; border-radius: 10px; }")
            
            return
        
        try:
            path_to_remove = Path(self.selected_path)
            if path_to_remove.exists():
                os.remove(path_to_remove)
            
            self.selected_path = None
            self.save_selection(None)
            
            self.reset_delete_button()
            self.refresh_gallery()
            
        except Exception as e:
            print(f"Ошибка при удалении: {e}")
            self.reset_delete_button()
    
    def reset_delete_button(self):
        self.confirm_delete = False
        self.add_del.setText("Удалить выбранный файл")
        self.add_del.setStyleSheet("")
    
    def save_selection(self, path):
        data = {}
        if os.path.exists(self.json_path):
            try:
                with open(self.json_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except: pass
        
        data["selected_file"] = path
        with open(self.json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
