from PySide6.QtWidgets import QGroupBox, QLabel, QVBoxLayout, QTableWidget
import functools

class PortfolioOverview(QGroupBox):
    def __init__(self):
        super().__init__()
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(QLabel("Net Liq"))

        self.net_liq = QLabel()
        self.layout().addWidget(self.net_liq)

    def update(self, pos_view_table: QTableWidget):
        values = [float(pos_view_table.item(i, 2).text()[1:]) for i in range(pos_view_table.rowCount())]
        new_val = functools.reduce(lambda x, y: x + y, values)
        self.net_liq.setText(f"${}")





def create_port_overview_widget():
    container = QGroupBox()
    container.setLayout(QVBoxLayout())
    container.add
