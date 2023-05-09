from PySide6.QtWidgets import QLineEdit, QGroupBox, QHBoxLayout, QPushButton
from PySide6.QtCore import QStringListModel
from dependencies import autocomplete as ac

class SearchBar(QGroupBox):
    def __init__(self, string_list):
        super().__init__()
        self.setStyleSheet('background-color: white;')
        self.setTitle("Find a Stock")

        self.setLayout(QHBoxLayout())
        self.search = QLineEdit()
        model = QStringListModel()
        model.setStringList(string_list)
        completer = ac.CustomQCompleter()
        completer.setModel(model)

        self.search.setCompleter(completer)
        self.layout().addWidget(self.search, 0)
        self.button = QPushButton("Chart")
        self.button.setEnabled(False)
        self.layout().addWidget(self.button, 0)
        completer.activated.connect(lambda: self.button.setEnabled(True))

        self.search.textChanged.connect(self.text_changed)

    def text_changed(self, txt):
        self.search.setText(txt.upper())