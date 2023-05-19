from PySide6.QtWidgets import QDialog, QGroupBox, QVBoxLayout

class StockInfoRecs(QDialog):
    def __init__(self):
        super().__init__()
        self.setStyleSheet('background-color: deepskyblue')
        self.analyst_rec_groupbox = QGroupBox(self)
        self.analyst_rec_groupbox.setStyleSheet('background-color: white')
        self.analyst_rec_groupbox.setTitle("Analyst Recommendations")
        self.analyst_rec_groupbox.setGeometry(10, 10, 310, 630)
        self.analyst_rec_groupbox.setVisible(False)
        self.analyst_rec_groupbox.setLayout(QVBoxLayout())
        self.iandi_groupbox = QGroupBox(self)
        self.iandi_groupbox.setStyleSheet('background-color: white')
        self.iandi_groupbox.setTitle("Insiders and Institutions")
        self.iandi_groupbox.setGeometry(330, 10, 470, 630)
        self.iandi_groupbox.setVisible(False)
        self.iandi_groupbox.setLayout(QVBoxLayout())
        self.mutfund_groupbox = QGroupBox(self)
        self.mutfund_groupbox.setStyleSheet('background-color: white')
        self.mutfund_groupbox.setTitle("Mutual Fund Holders")
        self.mutfund_groupbox.setGeometry(810, 10, 470, 630)
        self.mutfund_groupbox.setVisible(False)
        self.mutfund_groupbox.setLayout(QVBoxLayout())