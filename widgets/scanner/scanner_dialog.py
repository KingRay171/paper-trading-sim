from PySide6.QtWidgets import QDialog, QGridLayout


class ScannerDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setStyleSheet('background-color: deepskyblue')
        self.setLayout(QGridLayout())




