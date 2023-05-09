from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QComboBox, QCheckBox, QPushButton, QDialog, QVBoxLayout, QSpinBox, QDoubleSpinBox
from PySide6.QtGui import QIcon

SETTINGS_DIALOG_BTN_STYLESHEET = "QPushButton::hover{background-color: deepskyblue; color: white;}"

def change_indicator_panel(fn_name, value, settings, ta_list):
    """
    Changes the given indicator's panel (where it appears on the chart). Should
    be called whenever an indicator's panel combobox is changed.
    """
    for indicator in ta_list:
        if indicator[0] == fn_name:
            index = ta_list.index(indicator)
            new_tup = (fn_name, int(value))
            new_tup += (settings, )
            ta_list[index] = new_tup

def get_indicator_index(fn_name: str, ta_list):
    """
    Takes an indicator as a string and returns its index in the TA list
    """
    for indicator in ta_list:
        if indicator[0] == fn_name:
            return ta_list.index(indicator)
    raise ValueError(f"Indicator '{str}' is not in the list of TA")

def create_ta_widget(parent_widget: QWidget, name: str, selected_ta: list, fn_name: str, default_settings: list[tuple]):
    container = QWidget()
    container.setLayout(QHBoxLayout())
    container.layout().addWidget(QLabel(name))

    panel_cb = QComboBox()
    panel_cb.addItems([f"{i}" for i in range(0, 16)])
    panel_cb.currentTextChanged.connect(
        lambda state: change_indicator_panel(
            fn_name, state, selected_ta[get_indicator_index(fn_name, selected_ta)][2], selected_ta
        ) if checkbox.isChecked() else None
    )
    container.layout().addWidget(panel_cb)

    settings_button = QPushButton()
    settings_button.setVisible(False)
    size_retain = settings_button.sizePolicy()
    size_retain.setRetainSizeWhenHidden(True)
    settings_button.setSizePolicy(size_retain)
    settings_button.setIcon(QIcon('icons/gear.jpg'))

    container.enterEvent = lambda e: on_enter(e, container, settings_button)
    container.leaveEvent = lambda e: on_exit(e, container, settings_button)

    settings_button.clicked.connect(
        lambda: settings_button_clicked(parent_widget, name, default_settings, selected_ta, fn_name, checkbox, panel_cb)
    )

    container.layout().addWidget(settings_button)

    checkbox = QCheckBox()
    checkbox.clicked.connect(
        lambda: indicator_box_clicked(
            checkbox, panel_cb.currentIndex(), fn_name, [value for value, _ in default_settings], selected_ta
        )
    )
    container.layout().addWidget(checkbox)
    return container


def on_enter(_, container, settings_button):
    """
    Sets the background color of the technical indicator widget to gray when it is hovered over
    """
    settings_button.setVisible(True)
    container.setStyleSheet('background-color: #E3E3E3')

def on_exit(_, container, settings_button):
    """
    Sets the background color of the technical indicator indicator_widge to white when it is
    no longer being hovered over
    """
    settings_button.setVisible(False)
    container.setStyleSheet('background-color: white')

def indicator_box_clicked(box: QCheckBox, index: int, fn_name: str, settings: list, ta_list: list):
    """
    A function that is called whenever an indicator's checkbox is clicked.
    If the click is to add the indicator, an indicator tuple is created from the function
    string, selected index, and indicator settings and added to the global TA list.
    If the click is to remove the indicator, the global list is cleared and replaced with
    a new list that doesn't have the given indicator tuple.
    """
    if box.isChecked():
        ta_list.append((fn_name, index, settings))
    else:
        new_list = list(filter(lambda ta: ta[0] != fn_name, ta_list))
        ta_list.clear()
        ta_list.extend(new_list)

def settings_button_clicked(parent_widget: QWidget, name: str, default_settings: list[tuple], selected_ta: list, fn_name: str, widget_checkbox: QCheckBox, widget_combobox: QComboBox):
    wnd = QDialog(parent_widget)
    wnd.setWindowTitle(name)
    wnd.setLayout(QVBoxLayout())

    for i, (value, name) in enumerate(default_settings):
        setting_widget = QWidget()
        setting_widget.setLayout(QHBoxLayout())
        setting_widget.layout().addWidget(QLabel(name))
        if isinstance(value, int):
            setting_spinbox = QSpinBox()
            setting_spinbox.setValue(selected_ta[get_indicator_index(fn_name, selected_ta)][2][i] if widget_checkbox.isChecked() else value)
            setting_widget.layout().addWidget(setting_spinbox)
        elif isinstance(value, float):
            setting_spinbox = QDoubleSpinBox()
            setting_spinbox.setValue(selected_ta[get_indicator_index(fn_name, selected_ta)][2][i] if widget_checkbox.isChecked() else value)
            setting_widget.layout().addWidget(setting_spinbox)
        elif isinstance(value, bool):
            setting_checkbox = QCheckBox()
            setting_checkbox.setChecked(selected_ta[get_indicator_index(fn_name, selected_ta)][2][i] if widget_checkbox.isChecked() else value)
            setting_widget.layout().addWidget(setting_checkbox)
        wnd.layout().addWidget(setting_widget)

    defaults_button = QPushButton("Reset to Defualts")
    defaults_button.setStyleSheet(SETTINGS_DIALOG_BTN_STYLESHEET)
    defaults_button.clicked.connect(
        lambda: restore_default_settings(default_settings, wnd)
    )

    cancel_button = QPushButton("Cancel")
    cancel_button.setStyleSheet(SETTINGS_DIALOG_BTN_STYLESHEET)
    cancel_button.clicked.connect(lambda: wnd.done(0))

    ok_button = QPushButton("Save" if widget_checkbox.isChecked() else "Save and Add")
    ok_button.setStyleSheet(SETTINGS_DIALOG_BTN_STYLESHEET)
    ok_button.clicked.connect(
        lambda: ok_button_clicked(wnd, fn_name, widget_combobox, widget_checkbox, selected_ta)
    )

    buttons_widget = QWidget()
    buttons_widget.setLayout(QHBoxLayout())
    buttons_widget.layout().addWidget(defaults_button)
    buttons_widget.layout().addWidget(cancel_button)
    buttons_widget.layout().addWidget(ok_button)
    wnd.layout().addWidget(buttons_widget)

    wnd.exec_()

def restore_default_settings(default_settings, wnd):
    for (value, _), widget in zip(default_settings, wnd.children[:-1]):
        if isinstance(widget.children()[1], (QSpinBox, QDoubleSpinBox)):
            widget.children()[1].setValue(value)
        elif isinstance(widget.children()[1], QCheckBox):
            widget.children()[1].setChecked(value)

def ok_button_clicked(wnd: QDialog, fn_name: str, widget_combobox: QComboBox, widget_checkbox: QCheckBox, selected_ta: list):

    new_vals = [
        widget.value() if isinstance(widget, (QSpinBox, QDoubleSpinBox)) else widget.isChecked()
        for widget in [child.children()[2] for child in wnd.children()[1:-1]]
    ]
    settings_tuple = (fn_name, widget_combobox.currentIndex(), new_vals)
    if widget_checkbox.isChecked():
        selected_ta[get_indicator_index(fn_name, selected_ta)] = settings_tuple
    else:
        selected_ta.append(settings_tuple)
        widget_checkbox.setChecked(True)
    wnd.done(0)
