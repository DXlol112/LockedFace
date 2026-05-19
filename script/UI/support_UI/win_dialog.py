from PyQt6.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout
from PyQt6.QtCore import Qt
import os

class WinDialog(QWidget):
    def __init__(self, parent, massage, title="Actions") -> None:
        super().__init__(parent)
        self.setObjectName("overlay")

        self.setGeometry(parent.rect())

        self.setWindowFlag(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Widget)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)

        self.dialog = QWidget(self)
        self.dialog.setObjectName("modalDialog")
        self.dialog.setFixedSize(400, 200)

        title_layout = QHBoxLayout()
        self.title_label = QLabel(title)
        self.title_label.setObjectName("titleLabel")
        title_layout.addWidget(self.title_label)
        title_layout.addStretch()

        self.close_btn = QPushButton("X")
        self.close_btn.setObjectName("closeButton")
        self.close_btn.setFixedSize(30, 30)
        self.close_btn.clicked.connect(self._close)
        title_layout.addWidget(self.close_btn)

        self.msg_label = QLabel(massage)
        self.msg_label.setObjectName("messageLabel")
        self.msg_label.setWordWrap(True)
        self.msg_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout = QVBoxLayout(self.dialog)
        layout.addLayout(title_layout)
        layout.addWidget(self.msg_label)
        layout.addSpacing(20)

        self._center_dialog()
        self._load_stylesheet()
        self.raise_()
        self.show()

    def _center_dialog(self):
        parent_rect = self.parent().rect() # type: ignore
        x = (parent_rect.width() - self.dialog.width()) // 2
        y = (parent_rect.height() - self.dialog.height()) // 2
        self.dialog.move(x, y)

    def _load_stylesheet(self):
        style_path = "script/style/dialog_win.qss"
        if os.path.exists(style_path):
            try:
                with open(style_path, "r", encoding="utf-8") as f:
                    self.setStyleSheet(f.read())
            except FileNotFoundError:
                print(f"Ошибка: чтение файла стилей не удалось: {style_path}")
        else:
            print(f"Ошибка: файл стилей не найден: {style_path}")  
            
    def mousePressEvent(self, event): # type: ignore
        if not self.dialog.geometry().contains(event.position().toPoint()):
            self._close()
        super().mousePressEvent(event)
    
    def _close(self):
        self.hide()
        self.deleteLater()