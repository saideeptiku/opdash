
import pandas as pd
import yfinance as yf


# line plot object that is dynamically loaded
ticker = yf.Ticker("AAPL")
df = ticker.history(period="max")
print(df.reset_index())