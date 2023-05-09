#run this
import stock_prediction as ml
import os
#from stock_prediction import GRU
#from stock_prediction import input_data
#from stock_prediction import ModelAccessor

print("starting up")
def run_model(ticker):
  path = rf"{os.getcwd()}/models/" +ticker+".sav"
  isExist = os.path.exists(path)

  print(path)
  print(isExist)
  model_9 = 0

  next_time_steps, future_forecast, timesteps, stock_price = 0,0,0,0
  if(isExist):

    model_9 = ml.load_model(path)
    next_time_steps, future_forecast, timesteps, stock_price = ml.run_main(ticker, model_9)


  else:
    #model = torch.load(path)
    next_time_steps, future_forecast, timesteps, stock_price = ml.run_main(ticker)


  #print(model.runPredictions("ml_model/out.csv", 5, 30))
  return next_time_steps, future_forecast, timesteps, stock_price




next_time_steps, future_forecast, timesteps, stock_price =  run_model('AMZN')

#import PySide6.QtWidgets
from PySide6.QtCharts import (QChart, QChartView, QLineSeries, QDateTimeAxis)
from PySide6.QtGui  import QColor, QPixmap
from PySide6.QtWidgets import QApplication
import sys
from PySide6.QtCore import Qt

#1478
#need return chartview
_ =  QApplication()
print("wow1")
ptchart = QChart()
ptlineseries = QLineSeries()
ptlineseries.setName("stock")
ptchart.addSeries(ptlineseries)

x_axis = QDateTimeAxis()
x_axis.setTickCount(7)
x_axis.setFormat("yyyy-MM-dd")
x_axis.setTitleText("Date")
x_axis.setVisible(True)
ptchart.addAxis(x_axis, Qt.AlignmentFlag.AlignBottom)
print("wow2")

series = QLineSeries()
series2 = QLineSeries()


series.setName("Real")
series.setColor(QColor("blue"))
series.append(timesteps, stock_price)


series2.setName("Prediction")
series2.setColor(QColor("red"))
series2.append(next_time_steps, future_forecast)

ptchart.addSeries(series)
ptchart.addSeries(series2)

ptchartview = QChartView(ptchart)
print("wow")
