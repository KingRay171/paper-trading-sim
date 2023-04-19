
import yahooquery as yq
from dependencies import optionchain as oc
from PySide6.QtWidgets import QTableWidgetItem

print(type(yq.Ticker('BTC-USD').history('5d').iat[-1, 5]))
