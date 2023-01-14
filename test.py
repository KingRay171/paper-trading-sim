import yfinance as yf
import time

t1 = time.perf_counter()
yf.download("AAPL", period="5d")
t2 = time.perf_counter()
yf.download("AAPL", period="5d", interval="5d")
t3 = time.perf_counter()

print(f"original method: {t2 - t1} seconds")
print(f"new method: {t3 - t2} seconds")