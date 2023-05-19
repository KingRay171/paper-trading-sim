from PySide6.QtWidgets import QVBoxLayout

def clear_layout(layout: QVBoxLayout):
    """
    Removes all child widgets from the given layout
    """
    for idx in reversed(range(layout.count())):
        layout.itemAt(idx).widget().setParent(None)