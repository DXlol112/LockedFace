from PyQt6.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout
from PyQt6.QtCore import Qt


class StartPage(QWidget):
    def __init__(self, on_continue) -> None:
        super().__init__()

        layout = QVBoxLayout(self)

        text_title = QLabel("Перед использованием\n" \
                            "           программы ")
        text_title.setObjectName("text_title")

        text = QLabel("Поставьте камеру прямо на уровне глаз, направьте её ровно\nна лицо и обеспечьте яркое переднее освещение, избегая\nтеней и слепящего света сзади, чтобы ваше лицо было четко\nи полностью видно.")
        text.setObjectName("text")
        text.setAlignment(Qt.AlignmentFlag.AlignCenter)

        continue_btn = QPushButton("Продолжить")
        continue_btn.setObjectName("continue_btn")
        continue_btn.clicked.connect(on_continue)

        layout.addStretch()
        layout.addWidget(text_title, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(text)
        layout.addWidget(continue_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()
        