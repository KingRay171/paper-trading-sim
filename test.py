from PySide6.QtWidgets import QMainWindow, QPushButton, QApplication, QLabel, QWidget
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import mplfinance as mpf
from PySide6 import QtCore, QtWidgets
import numpy as np
from dependencies import stockchart as sc
import multiprocessing as mp

class MainWindow(QMainWindow):
     
     def __init__(self):
          self.anim = None
          super(MainWindow, self).__init__()
          btn = QPushButton('Click me!', self)
          btn.clicked.connect(self.onClick)

     def onClick(self):
          queue = mp.Queue()
          p = mp.Process(target=sc.startChart, args=("BTC-USD", "5m", [], False, True, False, True, queue, "1d"))
          p.start()
          mpf.show()

class SecondWindow(QMainWindow):
    def __init__(self):
         super(SecondWindow, self).__init__()
         self.main_widget = QtWidgets.QWidget(self)

         layout = QtWidgets.QVBoxLayout(self.main_widget)
         sc = MyMplCanvas(self.main_widget, width = 300, height = 300)
         layout.addWidget(sc)

class MyMplCanvas(FigureCanvas):

    def __init__(self, parent=None, width= 300, height= 300):
        fig = Figure(figsize=(width, height))
        self.axes = fig.add_subplot(111)

        self.compute_figure()

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def compute_figure(self):
        t = np.arange(0.0, 3.0, 0.01)
        s = np.sin(2*np.pi*t)
        self.axes.plot(t, s)

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    MW = MainWindow()
    MW.resize(500, 500)
    MW.show()
    sys.exit(app.exec_())