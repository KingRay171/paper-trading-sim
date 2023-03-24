import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from yahooquery import Ticker
import tensorflow as tf

def predict_stock_price(ticker_name, into_future=30, plot=True):
    """
    Returns two pandas dataframes: stock_df, future_stock_df.
    stock_df: stock's current data
    future_stock_df: stock's future predicted data

    ticker_name: stock or crypto ticker name from finance.yahoo.com (str)
    into_future: number of days into the future to predict stock (int)
    plot: If true, a plot of the predictions is graphed using matplotlib (boolean)
    """
    # Setup dataset hyperparameters
    # horizon = number of timesteps to predict into future
    # window = number of timesteps from past used to predict horizon
    horizon = 1
    window_size = 7

    # Download stock data
    ticker = Ticker(ticker_name)
    df = ticker.history(period="1y", interval="1d")
    df.reset_index(inplace=True)
    df = df[['date', 'adjclose']]

    # Create table of time and prices
    timesteps = pd.DataFrame(df['date'])
    df = df.set_index('date')
    stock_price = pd.DataFrame(df['adjclose'])

    # Prepare stock data with windowed columns
    stock_prices_windowed = df

    for i in range(window_size):
        stock_prices_windowed[f"adjclose+{i+1}"] = stock_prices_windowed["adjclose"].shift(periods=i+1)

    X = stock_prices_windowed.dropna().drop("adjclose", axis=1).astype(np.float32)
    y = stock_prices_windowed.dropna()["adjclose"].astype(np.float32)

    # Create TensorFlow Datasets
    batch_size = 1024
    epochs = 100
    features_dataset_all = tf.data.Dataset.from_tensor_slices(X)
    labels_dataset_all = tf.data.Dataset.from_tensor_slices(y)
    dataset_all = tf.data.Dataset.zip((features_dataset_all, labels_dataset_all))
    dataset_all = dataset_all.batch(batch_size).prefetch(tf.data.AUTOTUNE)

    # Create and train model
    tf.random.set_seed(42)

    model = tf.keras.Sequential([
        tf.keras.layers.Dense(128, activation="relu"),
        tf.keras.layers.Dense(128, activation="relu"),
        tf.keras.layers.Dense(horizon)
    ])

    model.compile(loss=tf.keras.losses.mae, optimizer=tf.keras.optimizers.Adam())

    model.fit(dataset_all, epochs=epochs, verbose=0)

    # Make future forecasts
    future_forecast = []
    last_window = y[-window_size:]

    for _ in range(into_future):
        future_pred = model.predict(tf.expand_dims(last_window, axis=0))
        future_forecast.append(tf.squeeze(future_pred).numpy())
        last_window = np.append(last_window, future_pred)[-window_size:]

    # Get future dates
    last_timestep = stock_price.index[-1]
    start_date = np.datetime64(last_timestep) + np.timedelta64(1, "D")
    end_date = np.datetime64(start_date) + np.timedelta64(into_future, "D")
    next_time_steps = np.arange(start_date, end_date, dtype="datetime64[D]")

    # Insert last timestep/final price so the graph doesn't look messed
    next_time_steps = np.insert(next_time_steps, 0, last_timestep)
    future_forecast = np.insert(future_forecast, 0, stock_price['adjclose'][-1])

    # Plot time series data
    if plot:
        plt.figure(figsize=(10, 7))
        plt.plot(timesteps, stock_price, "-", label="Actual Stock Price")
        plt.plot(next_time_steps, future_forecast, "-", label="Predicted Stock Price")
        plt.xlabel("Time")
        plt.ylabel("Stock Price")
        plt.legend(fontsize=14)
        plt.grid(True)
        plt.show()

    # Return future forecasts as dataframe
    stock_df = pd.DataFrame({'date': list(timesteps['date']), 'adjclose': list(stock_price['adjclose'])}).set_index('date')
    future_stock_df = pd.DataFrame({'date': next_time_steps, 'adjclose': future_forecast}).set_index('date')
    return stock_df, future_stock_df

# Example usage
predict_stock_price(ticker_name='BTC-USD')
