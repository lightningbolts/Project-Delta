import yfinance as yf
import pandas as pd

def get_stock_data(ticker, period="1y"):
    """
    Fetches historical stock data for the given ticker symbol.
    """
    stock_data = yf.download(ticker, period=period)
    return stock_data

def calculate_sma(data, window):
    """
    Calculates the Simple Moving Average (SMA).
    """
    return data['Close'].rolling(window=window).mean()

def trading_strategy(stock_data):
    """
    Implements a simple moving average crossover strategy.
    """
    # Calculate short-term and long-term SMAs
    stock_data['SMA_50'] = calculate_sma(stock_data, 50)
    stock_data['SMA_200'] = calculate_sma(stock_data, 200)

    # Generate signals
    stock_data['Signal'] = 0
    stock_data['Signal'][50:] = [
        1 if stock_data['SMA_50'][i] > stock_data['SMA_200'][i] else -1
        for i in range(50, len(stock_data))
    ]

    return stock_data

def generate_recommendation(ticker):
    """
    Generates a buy/sell recommendation based on the trading strategy.
    """
    # Fetch data
    stock_data = get_stock_data(ticker)

    # Apply strategy
    stock_data = trading_strategy(stock_data)

    # Current recommendation based on the last signal
    last_signal = stock_data['Signal'].iloc[-1]

    if last_signal == 1:
        return "Buy"
    elif last_signal == -1:
        return "Sell"
    else:
        return "Hold"

if __name__ == "__main__":
    ticker = input("Enter the stock ticker symbol: ").upper()
    recommendation = generate_recommendation(ticker)
    print(f"Recommendation for {ticker}: {recommendation}")