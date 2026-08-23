from PyQt6.QtCore import QEvent, Qt
from PyQt6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget


class StartPage(QWidget):
    def __init__(self, on_continue) -> None:  # type: ignore[no-untyped-def]
        super().__init__()

        layout = QVBoxLayout(self)

        self.text_title = QLabel()
        self.text_title.setObjectName("text_title")
        self.text_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.text = QLabel()
        self.text.setObjectName("text")
        self.text.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.continue_button = QPushButton()
        self.continue_button.setObjectName("continue_btn")
        self.continue_button.clicked.connect(on_continue)

        layout.addStretch()
        layout.addWidget(self.text_title, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.text)
        layout.addWidget(self.continue_button, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()

        self.retranslate_ui()

    def retranslate_ui(self) -> None:
        self.text_title.setText(self.tr("Перед использованием\nпрограммы"))
        self.text.setText(
            self.tr(
                "Поставьте камеру прямо на уровне глаз и направьте её на лицо.\n"
                "Обеспечьте яркое переднее освещение, избегайте теней и света сзади,\n"
                "чтобы лицо было чётко и полностью видно."
            )
        )
        self.continue_button.setText(self.tr("Продолжить"))

    def changeEvent(self, event: QEvent) -> None:  # pyright: ignore[reportIncompatibleMethodOverride] # noqa: N802
        if event.type() == QEvent.Type.LanguageChange:
            self.retranslate_ui()
        super().changeEvent(event)
