#run this
from dependencies import stock_prediction as ml
import os
import datetime
from datetime import date
from PySide6.QtWidgets import QApplication, QWidget, QDialog, QHBoxLayout
from PySide6.QtCore import Qt

import datetime
from datetime import date
from PySide6.QtWidgets import QApplication, QWidget, QDialog, QHBoxLayout
from PySide6.QtCore import Qt

#from stock_prediction import GRU
#from stock_prediction import input_data
#from stock_prediction import ModelAccessor
def run(ticker):
  print("starting up")
  def run_model(ticker):
    path = rf"{os.getcwd()}\\dependencies\\models\\" +ticker+".sav"
    isExist = os.path.exists(path)

    print(path)
    print(isExist)
    model_9 = 0

    next_time_steps, future_forecast, timesteps, stock_price = 0,0,0,0

    next_time_steps, future_forecast, timesteps, stock_price = ml.run_main(ticker)


    #print(model.runPredictions("ml_model/out.csv", 5, 30))
    return next_time_steps, future_forecast, timesteps, stock_price




  next_time_steps, future_forecast, timesteps, stock_price =  run_model(ticker)

  #import PySide6.QtWidgets
  from PySide6.QtCharts import (QChart, QChartView, QLineSeries, QDateTimeAxis)
  from PySide6.QtGui  import QColor, QPixmap
  from PySide6.QtCore import QDateTime
  from PySide6.QtWidgets import QApplication
  import sys
  from PySide6.QtCore import Qt

  #1478
  #need return chartview
  #print("wow1")
  ptchart = QChart()
  ptlineseries = QLineSeries()
  ptlineseries.setName("stock")
  ptchart.addSeries(ptlineseries)

  x_axis = QDateTimeAxis()
  x_axis.setTickCount(7)
  x_axis.setFormat("yyyy-MM-dd")
  x_axis.setTitleText("Date")
  x_axis.setVisible(True)


  #print("wow2")

  series = QLineSeries()
  series2 = QLineSeries()



  series.setName("Real")
  series.setColor(QColor("blue"))

  series2.setName("Prediction")
  series2.setColor(QColor("red"))


  timesteps = timesteps.values.ravel()
  stock_price = stock_price.values.ravel()

  # getting length of list
  length = len(timesteps)

  #setRange(min, max)
  #print(type(timesteps[0]))

  import datetime

  min_x = datetime.datetime.combine(timesteps[0], datetime.time.min).timestamp()*1000
  min_y = stock_price.min()
  max_y = stock_price.max()
  #min1 = min
  for i in range(length):
    time = datetime.datetime.combine(timesteps[i], datetime.time.min).timestamp()*1000
    #print(timesteps[i])
    #print(time)
    #if(time<min):
    #  print("this is not supposed to happem")
    #  min1 = time
    series.append(time, stock_price[i])

  length = len(next_time_steps)
  #print("start part 2")


  for i in range(length):
    time = next_time_steps[i].astype("datetime64[s]").astype('float')*1000
    #print(time)
    series2.append(time, future_forecast[i])
    max_x = time

  if(max(future_forecast)>max_y):
    max_y = max(future_forecast)
  if(min(future_forecast)<min_y):
    min_y = min(future_forecast)


  ptchart.addSeries(series)
  ptchart.addSeries(series2)

  ptchart.createDefaultAxes()
  ptchart.axes(Qt.Orientation.Horizontal)[0].hide()

  from PySide6.QtCore import  QDateTime


  min_x = QDateTime.fromSecsSinceEpoch(int(min_x/1000))
  max_x = QDateTime.fromSecsSinceEpoch(int(max_x/1000))


  x_axis.setRange(min_x, max_x)
  ptchart.axes(Qt.Orientation.Vertical)[0].setRange(min_y*0.9, max_y*1.1)

  ptchart.addAxis(x_axis, Qt.AlignmentFlag.AlignBottom)
  series.attachAxis(x_axis)


  ptchartview = QChartView(ptchart)
  w = QDialog()
  w.setLayout(QHBoxLayout())
  w.layout().addWidget(ptchartview)
  w.exec()

  #print("wow")
