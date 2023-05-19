from PySide6.QtWidgets import QDialog, QGroupBox, QLineEdit, QPushButton, QVBoxLayout, QScrollArea, QWidget
from PySide6.QtGui import QFont
from PySide6.QtCore import QStringListModel

from dependencies import autocomplete as ac

class StockInfoMain(QDialog):
    def __init__(self, string_list):
        super().__init__()
        self.setStyleSheet('background-color: deepskyblue')
        self.completer = ac.CustomQCompleter()
        self.model = QStringListModel()
        self.model.setStringList(string_list)
        self.completer.setModel(self.model)

        self.searchbar_gb = QGroupBox(self)
        self.searchbar_gb.setStyleSheet('background-color: white;')
        self.searchbar_gb.setTitle("Find a Stock")
        self.searchbar_gb.setGeometry(10, 10, 960, 70)
        self.searchbar_gb.searchBar = QLineEdit(self.searchbar_gb)
        self.searchbar_gb.searchBar.setGeometry(10, 20, 850, 40)
        self.searchbar_gb.searchBar.textChanged.connect(self.search_text_changed)
        self.searchbar_gb.searchBar.setFont(QFont('arial', 10))
        self.searchbar_gb.searchBar.setCompleter(self.completer)
        self.searchbar_gb.search_button = QPushButton(self.searchbar_gb)
        self.searchbar_gb.search_button.setGeometry(870, 20, 80, 40)
        self.searchbar_gb.search_button.setText("Show Info")

        self.asset_info_gb = QGroupBox(self)
        self.asset_info_gb.setStyleSheet('background-color: white')
        self.asset_info_gb.setTitle("Asset Profile")
        self.asset_info_gb.setGeometry(10, 90, 310, 550)
        self.asset_info_gb.setVisible(False)
        self.asset_info_gb.content_container = QScrollArea(self.asset_info_gb)
        self.assetinfo_scrollarea_widget = QWidget()
        self.assetinfo_scrollarea_widget.resize(300, 800)
        self.assetinfo_scrollarea_widget.setLayout(QVBoxLayout())
        self.asset_info_gb.content_container.setWidget(self.assetinfo_scrollarea_widget)
        self.asset_info_gb.content_container.setGeometry(5, 15, 305, 520)

        self.about_groupbox = QGroupBox(self)
        self.about_groupbox.setStyleSheet('background-color: white')
        self.about_groupbox.setTitle("About the Asset")
        self.about_groupbox.setGeometry(330, 90, 540, 550)
        self.about_groupbox.setVisible(False)
        self.about_groupbox.content_container = QScrollArea(self.about_groupbox)
        self.about_scrollarea_widget = QWidget()
        self.about_scrollarea_widget.resize(540, 800)
        self.about_scrollarea_widget.setLayout(QVBoxLayout())
        self.about_groupbox.content_container.setWidget(self.about_scrollarea_widget)
        self.about_groupbox.content_container.setGeometry(5, 15, 530, 520)

        self.news_groupbox = QGroupBox(self)
        self.news_groupbox.setStyleSheet('background-color: white')
        self.news_groupbox.setTitle("News")
        self.news_groupbox.setGeometry(880, 90, 400, 550)
        self.news_groupbox.setVisible(False)
        self.news_groupbox.setLayout(QVBoxLayout())

    def search_text_changed(self, txt: str):
        """
        Executed when text is typed into the search bar on the "Chart Stocks" tab.
        The function takes the entered text and appends it to the search bar.
        """
        self.searchbar_gb.searchBar.setText(txt.upper())

