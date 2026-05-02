import yfinance as yf
stock = yf.Ticker("AAPL")
try:
    print(stock.fast_info['lastPrice'])
except Exception as e:
    print(e)
