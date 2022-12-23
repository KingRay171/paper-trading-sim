from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QDialog, QPushButton, QVBoxLayout, QApplication, QSplashScreen
from PySide6.QtCore import QTimer
import sys
from time import sleep


if __name__ == '__main__':
    app = QApplication(sys.argv)
    splash = QSplashScreen(QPixmap('splash.png'))
    splash.show()
    sleep(4)
    splash.close()
    splash = QSplashScreen(QPixmap('stonks.jpg'))
    splash.show()
    sleep(4)
    splash = QSplashScreen(QPixmap('sbf.jpg'))
    splash.show()
    sleep(4)
    splash = QSplashScreen(QPixmap('nyse.jpg'))
    splash.show()
    sleep(4)
    sys.exit(app.exec_())