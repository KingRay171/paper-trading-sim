from PySide6.QtWidgets import QDialog, QComboBox, QLabel, QPushButton
from dependencies import readassets as ra
import xml.etree.ElementTree as et

class SettingsTab(QDialog):
    def __init__(self):
        super().__init__()
        up_colors = ['Green', 'Red', 'Cyan', 'Purple']
        down_colors = ['Green', 'Red', 'Cyan', 'Purple']
        chart_styles = ['binance', 'blueskies', 'brasil', 'charles', 'checkers', 'classic',
                        'default', 'ibd', 'kenan', 'mike', 'nightclouds', 'sas', 'starsandstripes', 'yahoo']

        up_color = ra.get_xml_data(r'assets\settings.xml', 'upcolor')
        down_color = ra.get_xml_data(r'assets\settings.xml', 'downcolor')
        base_style = ra.get_xml_data(r'assets\settings.xml', 'basestyle')

        up_colors.remove(up_color[0].text.capitalize())
        up_colors.insert(0, up_color[0].text.capitalize())
        down_colors.remove(down_color[0].text.capitalize())
        down_colors.insert(0, down_color[0].text.capitalize())
        chart_styles.remove(base_style[0].text)
        chart_styles.insert(0, base_style[0].text)

        self.setStyleSheet('background-color: deepskyblue;')
        self.up_color_combobox = QComboBox(self)
        self.up_color_label = QLabel(self)
        self.up_color_label.setText("Up Candle Color:")
        self.up_color_label.setGeometry(10, 10, 200, 40)
        self.up_color_combobox.addItems(up_colors)
        self.up_color_combobox.setGeometry(10, 50, 200, 40)
        # label and dropdown menu to set the color of down candles
        self.down_color_combobox = QComboBox(self)
        self.down_color_label = QLabel(self)
        self.down_color_label.setText("Down Candle Color:")
        self.down_color_label.setGeometry(220, 10, 200, 40)
        self.down_color_combobox.addItems(down_colors)
        self.down_color_combobox.setGeometry(220, 50, 200, 40)
        # label and dropdown menu to set the chart style
        self.chart_style_combobox = QComboBox(self)
        self.chart_style_label = QLabel(self)
        self.chart_style_label.setText("Chart Style:")
        self.chart_style_label.setGeometry(430, 10, 200, 40)
        self.chart_style_combobox.addItems(chart_styles)
        self.chart_style_combobox.setGeometry(430, 50, 200, 40)
        # button to apply changes
        self.apply_button = QPushButton(self)
        self.apply_button.setText("Apply")
        self.apply_button.setGeometry(450, 500, 100, 50)
        self.apply_button.clicked.connect(self.apply_settings_changes)

    def apply_settings_changes(self):
        """Updates assets/settings.xml with the currently selected settings in the GUI"""
        # gets currently selected settings
        color_up = self.up_color_combobox.currentText()
        color_down = self.down_color_combobox.currentText()
        style = self.chart_style_combobox.currentText()

        # parses XML file into an ElementTree
        tree = et.parse('assets/settings.xml')


        # replaces old data in the file with the current data
        for color in tree.getroot().iter('upcolor'):
            color.text = color_up

        for color in tree.getroot().iter('downcolor'):
            color.text = color_down

        for chart_style in tree.getroot().iter('basestyle'):
            chart_style.text = style

        tree.write('assets/settings.xml')