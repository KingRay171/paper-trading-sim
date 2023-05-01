import numpy as np
import pandas as pd

import pickle
import matplotlib.pyplot as plt
from yahooquery import Ticker
import tensorflow as tf
import os

# Setup dataset hyperparameters
# horizon = number of timesteps to predict into future
# window = number of timesteps from past used to predict horizon
HORIZON = 1
WINDOW_SIZE = 7
# How many timesteps to predict into the future?
INTO_FUTURE = 30 # days (don't recommend going over 30)

def get_data(ticker_name):
  # Download stock data
  ticker = Ticker(ticker_name)
  df = ticker.history(period="1y", interval="1d")   # max
  df.reset_index(inplace=True)
  df = df[['date', 'adjclose']]
  
  # Create table of time and prices
  timesteps = pd.DataFrame(df['date'])
  df = df.set_index('date')
  stock_price = pd.DataFrame(df['adjclose'])
  return df, stock_price, timesteps

def process_data(X, y):
  # 1. Turn X and y into tensor Datasets
  features_dataset_all = tf.data.Dataset.from_tensor_slices(X)
  labels_dataset_all = tf.data.Dataset.from_tensor_slices(y)
  
  # 2. Combine features & labels
  dataset_all = tf.data.Dataset.zip((features_dataset_all, labels_dataset_all))
  
  # 3. Batch and prefetch for optimal performance
  BATCH_SIZE = 1024 # taken from Appendix D in N-BEATS paper
  dataset_all = dataset_all.batch(BATCH_SIZE).prefetch(tf.data.AUTOTUNE)
  return dataset_all

def make_model(dataset_all, ticker):
# Create model
  tf.random.set_seed(42)
  model_9 = tf.keras.Sequential([
  tf.keras.layers.Dense(128, activation="relu"),
  tf.keras.layers.Dense(128, activation="relu"),
  tf.keras.layers.Dense(HORIZON)
])

  # Compile
  model_9.compile(loss=tf.keras.losses.mae,
                  optimizer=tf.keras.optimizers.Adam())
  
  # Fit model on all of the data to make future forecasts
  model_9.fit(dataset_all,
              epochs=100)
  filename = ticker+'.sav'
  
  path = rf"{os.getcwd()}/models/"+filename
  with open( path, 'wb') as f:
    pickle.dump(model_9, f)
  return model_9

def load_model(filename):
  return pickle.load(open(filename, 'rb'))

def get_future_dates(start_date, into_future, offset=1):
  """
  Returns array of datetime values from ranging from start_date to start_date+horizon.

  start_date: date to start range (np.datetime64)
  into_future: number of days to add onto start date for range (int)
  offset: number of days to offset start_date by (default 1)
  """
  start_date = np.datetime64(start_date) + np.timedelta64(offset, "D") # specify start date, "D" stands for day
  end_date = np.datetime64(start_date) + np.timedelta64(into_future, "D") # specify end date
  return np.arange(start_date, end_date, dtype="datetime64[D]") # return a date range between start date and end date

# Create a function to plot time series data
def plot_time_series(timesteps, values, format='.', start=0, end=None, label=None):
    """
    Plots a timesteps (a series of points in time) against values (a series of values across timesteps).

    Parameters
    ---------
    timesteps : array of timesteps
    values : array of values across time
    format : style of plot, default "."
    start : where to start the plot (setting a value will index from start of timesteps & values)
    end : where to end the plot (setting a value will index from end of timesteps & values)
    label : label to show on plot of values
    """
    # Plot the series
    plt.plot(timesteps[start:end], values[start:end], format, label=label)
    plt.xlabel("Time")
    plt.ylabel("Stock Price")
    if label:
        plt.legend(fontsize=14)  # make label bigger
    plt.grid(True)

# 1. Create function to make predictions into the future
def make_future_forecast(values, model, into_future, window_size=WINDOW_SIZE) -> list:
  """
  Makes future forecasts into_future steps after values ends.
  Returns future forecasts as list of floats.
  """
  # 2. Make an empty list for future forecasts/prepare data to forecast on
  future_forecast = []
  last_window = values[-WINDOW_SIZE:]  # only want preds from the last window (this will get updated)

  # 3. Make INTO_FUTURE number of predictions, altering the data which gets predicted on each time
  for _ in range(into_future):
    # Predict on last window then append it again, again, again (model starts to make forecasts on its own forecasts)
    future_pred = model.predict(tf.expand_dims(last_window, axis=0))

    # Append predictions to future_forecast
    future_forecast.append(tf.squeeze(future_pred).numpy())

    # Update last window with new pred and get WINDOW_SIZE most recent preds (model was trained on WINDOW_SIZE windows)
    last_window = np.append(last_window, future_pred)[-WINDOW_SIZE:]

  return future_forecast

def run_main(ticker, model_9=None):
  df, stock_price, timesteps = get_data(ticker)
  # Make a copy of the stock historical data with block reward feature
  stock_prices_windowed = df
  
  
  #window stuffs
  # Add windowed columns [training data] -> [label]
  # [0, 1, 2, 3, 4, 5, 6] -> [7]
  # [1, 2, 3, 4, 5, 6, 7] -> [8]
  # [2, 3, 4, 5, 6, 7, 8] -> [9]
  for i in range(WINDOW_SIZE): # Shift values for each step in WINDOW_SIZE
    stock_prices_windowed[f"adjclose+{i+1}"] = stock_prices_windowed["adjclose"].shift(periods=i+1)
  
  X = stock_prices_windowed.dropna().drop("adjclose", axis=1).astype(np.float32)
  y = stock_prices_windowed.dropna()["adjclose"].astype(np.float32)
  
  dataset_all = process_data(X, y)
  
  if(model_9 == None):
    print("I start training")
    model_9 = make_model(dataset_all, ticker)
  else:
    print("I already exist")
  
  # Windows and labels ready. Now turn them into performance optimized TensorFlow Datasets by
  
  # Last timestep of timesteps (currently in np.datetime64 format)
  last_timestep = stock_price.index[-1]
  
  # Get next two weeks of timesteps
  next_time_steps = get_future_dates(start_date=last_timestep,
                                     into_future=INTO_FUTURE)
  
  # Make forecasts into future of the price of Bitcoin
  future_forecast = make_future_forecast(values=y,
                                         model=model_9,
                                         into_future=INTO_FUTURE,
                                         window_size=WINDOW_SIZE)
  
  
  # Insert last timestep/final price so the graph doesn't look messed
  next_time_steps = np.insert(next_time_steps, 0, last_timestep)
  future_forecast = np.insert(future_forecast, 0, stock_price['adjclose'][-1])
    
  
  
  
  # Plot future price predictions of stock
  plt.figure(figsize=(5, 3))
  print(stock_price.index, len(stock_price.index))
  print(timesteps, len(timesteps))
  plot_time_series(timesteps, stock_price, start=0, format="-", label="Actual Stock Price")
  plot_time_series(next_time_steps, future_forecast, format="-", label="Predicted Stock Price")
  #plt.show()
  return plt
  
