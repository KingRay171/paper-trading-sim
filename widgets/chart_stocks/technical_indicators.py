from PySide6.QtWidgets import QDialog, QGroupBox

class IndicatorsWidget(QDialog):
    def __init__(self):
        super().__init__()
        combobox_items = [f"{I}" for i in range(0, 16)]

        self.momentum_gb = QGroupBox()
        self.momentum_gb.setTitle('Momentum Indicators')
        self.momentum_gb.setStyleSheet('background-color: white;')

