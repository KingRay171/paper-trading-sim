from pytestqt.qtbot import QtBot
from widgets.portfolio.watchlist import Watchlist
from PySide6.QtCore import Qt

def test_init(qtbot: QtBot):
    watchlist = Watchlist(['SPY', 'QQQ', 'DIA'])
    qtbot.addWidget(watchlist)
    watchlist.update(['SPY', "QQQ", "DIA"])
    qtbot.mouseClick(watchlist.table, Qt.MouseButton.LeftButton)
    qtbot.keyPress(watchlist.table, Qt.Key.Key_Delete)


    assert watchlist.table.rowCount() == 3

    assert watchlist.table.item(1, 0).text() != ""



