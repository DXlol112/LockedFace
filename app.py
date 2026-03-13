import PyQt6.QtWidgets as qtw
from PyQt6.QtGui import QIcon

class HelloMainWindow(qtw.QMainWindow):
    def __int__(self):
        super().__init__()

        self.setWindowTitle("Maintaining-attention-at-work")
        self.setGeometry(100,100, 800, 600)
        self.setWindowIcon(QIcon('app_icon.jpg'))



app = qtw.QApplication([])

window = HelloMainWindow()
window.show()

