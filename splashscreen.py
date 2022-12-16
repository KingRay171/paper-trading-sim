from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QDialog, QPushButton, QVBoxLayout, QApplication, QSplashScreen
from PySide6.QtCore import QTimer
import sys

class Dialog(QDialog):
    def __init__(self, parent=None):
        super(Dialog, self).__init__(parent)

        self.b1 = QPushButton('Display screensaver')
        self.b1.clicked.connect(self.flashSplash)

        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.addWidget(self.b1)

    def flashSplash(self):
        self.splash = QSplashScreen(QPixmap('splash.png'))
        self.splash.show()
        QTimer.singleShot(4000, self.splash.close)

        self.splash = QSplashScreen(QPixmap('stonks.jpg'))
        self.splash.show()
        QTimer.singleShot(4000, self.splash.close)

        self.splash = QSplashScreen(QPixmap('sbf.jpg'))
        self.splash.show()
        QTimer.singleShot(4000, self.splash.close)

        self.splash = QSplashScreen(QPixmap('nyse.jpg'))
        self.splash.show()
        QTimer.singleShot(4000, self.splash.close)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = Dialog()
    main.show()
    sys.exit(app.exec_())