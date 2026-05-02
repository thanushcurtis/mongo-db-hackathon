import yfinance as yf
print("Ticker.history:")
try:
    print(yf.Ticker("AAPL").history(period="1d"))
except Exception as e:
    print(e)
    
print("\nyf.download:")
try:
    print(yf.download("AAPL", period="1d"))
except Exception as e:
    print(e)
