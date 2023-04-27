from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QComboBox

class TAWidget(QWidget):
    def __init__(self, parent_widget: QWidget, name: str, selected_ta: list):
        super().__init__()
        self.setLayout(QHBoxLayout())
        self.layout().addWidget(QLabel(name))

        self.panel_cb = QComboBox()
        self.panel_cb.addItems([f"{i}" for i in range(0, 16)])
        self.panel_cb.currentTextChanged.connect(
            lambda state: change
        )



