from PySide6.QtWidgets import QDialog, QGroupBox, QPushButton, QLabel
from PySide6.QtGui import QIcon, QFont, QEnterEvent
from PySide6.QtCore import QSize
import os

class UnconStratsTab(QDialog):
    def __init__(self):
        super().__init__()
        self.setStyleSheet('background-color: deepskyblue')

        self.cramer_gb = QGroupBox(self)
        self.cramer_gb.setTitle('Inverse Jim Cramer')
        self.cramer_gb.setGeometry(10, 20, 350, 350)
        self.cramer_gb.setStyleSheet('background-color: white')

        self.cramer_gb.cramer_btn = QPushButton(self.cramer_gb)
        self.cramer_gb.cramer_btn.setIcon(QIcon(rf"{os.getcwd()}\icons\index.jpg"))
        self.cramer_gb.cramer_btn.setIconSize(QSize(200, 300))
        self.cramer_gb.cramer_btn.setGeometry(10, 20, 300, 190)
        self.cramer_gb.cramer_btn.setEnabled(False)

        self.cramer_gb.cramer_btn.enterEvent = lambda e: self.uncon_strat_enter(
            e, self.cramer_gb.cramer_btn
        )
        self.cramer_gb.cramer_btn.leaveEvent = lambda e: self.uncon_strat_leave(
            e, self.cramer_gb.cramer_btn
        )

        self.cramer_gb.cramer_label_header = QLabel(self.cramer_gb)
        self.cramer_gb.cramer_label_header.setText('Inverse Cramer Scanner')
        self.cramer_gb.cramer_label_header.setGeometry(10, 240, 300, 30)
        self.cramer_gb.cramer_label_header.setFont(QFont('arial', 20))

        self.cramer_gb.cramer_label_text = QLabel(self.cramer_gb)
        self.cramer_gb.cramer_label_text.setText(
            "Find CNBC analyst Jim Cramer's most recent buy and sell recommendations"
        )
        self.cramer_gb.cramer_label_text.setGeometry(10, 270, 300, 50)
        self.cramer_gb.cramer_label_text.setWordWrap(True)


        self.wsb_gb = QGroupBox(self)
        self.wsb_gb.setTitle('WSB Scanner')
        self.wsb_gb.setGeometry(500, 20, 350, 350)
        self.wsb_gb.setStyleSheet('background-color: white')

        self.wsb_gb.wsb_btn = QPushButton(self.wsb_gb)
        self.wsb_gb.wsb_btn.setIcon(QIcon(rf"{os.getcwd()}\icons\index.jpg"))
        self.wsb_gb.wsb_btn.setIconSize(QSize(200, 300))
        self.wsb_gb.wsb_btn.setGeometry(10, 20, 300, 190)
        self.wsb_gb.wsb_btn.setEnabled(False)

        self.wsb_gb.wsb_btn.enterEvent = lambda e: self.uncon_strat_enter(
            e, self.wsb_gb.wsb_btn
        )
        self.wsb_gb.wsb_btn.leaveEvent = lambda e: self.uncon_strat_leave(
            e, self.wsb_gb.wsb_btn
        )


        self.wsb_gb.wsb_label_header = QLabel(self.wsb_gb)
        self.wsb_gb.wsb_label_header.setText('WallStreetBets Trending')
        self.wsb_gb.wsb_label_header.setGeometry(10, 240, 300, 30)
        self.wsb_gb.wsb_label_header.setFont(QFont('arial', 20))

        self.wsb_gb.wsb_label_text = QLabel(self.wsb_gb)
        self.wsb_gb.wsb_label_text.setText(
            "Find tickers that are recieving the most attention from r/WallStreetBets"
        )
        self.wsb_gb.wsb_label_text.setGeometry(10, 270, 300, 50)
        self.wsb_gb.wsb_label_text.setWordWrap(True)

        self.google_gb = QGroupBox(self)
        self.google_gb.setTitle('Google Trends Scanner')
        self.google_gb.setGeometry(250, 400, 350, 350)
        self.google_gb.setStyleSheet('background-color: white')

        self.google_gb.google_btn = QPushButton(self.google_gb)
        self.google_gb.google_btn.setIcon(QIcon(rf"{os.getcwd()}\icons\index.jpg"))
        self.google_gb.google_btn.setIconSize(QSize(200, 300))
        self.google_gb.google_btn.setGeometry(10, 20, 300, 190)
        self.google_gb.google_btn.setEnabled(False)


        self.google_gb.google_btn.enterEvent = lambda e: self.uncon_strat_enter(
            e, self.google_gb.google_btn
        )
        self.google_gb.google_btn.leaveEvent = lambda e: self.uncon_strat_leave(
            e, self.google_gb.google_btn
        )


        self.google_gb.google_label_header = QLabel(self.google_gb)
        self.google_gb.google_label_header.setText('Google Trending')
        self.google_gb.google_label_header.setGeometry(10, 240, 300, 30)
        self.google_gb.google_label_header.setFont(QFont('arial', 20))

        self.google_gb.google_label_text = QLabel(self.google_gb)
        self.google_gb.google_label_text.setText(
            "Find tickers that are recieving the most search interest"
        )
        self.google_gb.google_label_text.setGeometry(10, 270, 300, 50)
        self.google_gb.google_label_text.setWordWrap(True)

    def uncon_strat_enter(self, _: QEnterEvent, button: QPushButton):
        """
        Triggered when one of the unconventional strategy buttons is entered by the mouse
        """

        button.setEnabled(True)
        button.setStyleSheet("border: 3px solid green;")


    def uncon_strat_leave(self, _, button: QPushButton):
        button.setEnabled(False)
        button.setStyleSheet("")
