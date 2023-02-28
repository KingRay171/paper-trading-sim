def main():
  stock_list = Volume()
  # EXPORTING RESULTS IS OPTIONAL
  # Export the screener results to .csv
  stock_list.to_csv("stock.csv")

  # Create a SQLite database
  stock_list.to_sqlite("stock.sqlite3")
  #
  for stock in stock_list[0:19]:  # Loop through 10th - 20th stocks
    print(stock['Ticker'], stock['Volume']) # Print symbol

#crypto order book
import requests

def cryptoBids(ticket, number):
  data = requests.get("https://api.pro.coinbase.com/products/"+ticket+"-USD/book?level=2").json()
  bids = data["bids"]
  bids = bids[0:number]
  return bids

def cryptoAsks(ticket, number):
  data = requests.get("https://api.pro.coinbase.com/products/"+ticket+"-USD/book?level=2").json()
  asks = data["asks"]
  asks = asks[0:number]
  return asks


#stock scanner
# from https://github.com/mariostoev/finviz
from finviz.screener import Screener
filters = ['exch_nasd', 'idx_sp500']  # Shows companies in NASDAQ which are in the S&P500

def highestGrowth():
  stock_list = Screener(filters=filters, table='Performance', order='-change')  # Get the performance table and sort it by change ascending
  return stock_list

def highestLoss():
  stock_list = Screener(filters=filters, table='Performance', order='change')  # Get the performance table and sort it by change ascending
  return stock_list

def highestVolitility():
  stock_list = Screener(filters=filters, table='Performance', order='-volatility1w')  # Get the performance table and sort it by change ascending
  return stock_list

def Volume():
  stock_list = Screener(filters=filters, table='Performance', order='volume')  # Get the performance table and sort it by change ascending
  return stock_list

main()
