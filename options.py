import yfinance as yf
import pandas as pd

def get_stock_data(ticker):
    """
    Fetches current stock data for the given ticker symbol.
    """
    stock = yf.Ticker(ticker)
    stock_price = stock.history(period="1d").iloc[-1]['Close']
    return stock_price, stock.options

def get_options_data(ticker, expiration):
    """
    Fetches options data for a specific expiration date.
    """
    stock = yf.Ticker(ticker)
    options = stock.option_chain(expiration)
    return options.calls, options.puts

def filter_options(options, stock_price, option_type="call", max_strike_diff=5, min_open_interest=100):
    """
    Filters options based on strike price proximity to the current stock price and open interest.
    """
    if option_type == "call":
        filtered = options[(options['strike'] > stock_price) &
                           (options['strike'] <= stock_price + max_strike_diff) &
                           (options['openInterest'] >= min_open_interest)]
    else:
        filtered = options[(options['strike'] < stock_price) &
                           (options['strike'] >= stock_price - max_strike_diff) &
                           (options['openInterest'] >= min_open_interest)]

    return filtered

def select_option(filtered_options):
    """
    Selects the best option to buy based on criteria like implied volatility and Theta.
    """
    if not filtered_options.empty:
        best_option = filtered_options.sort_values(by=['impliedVolatility']).iloc[0]
        return best_option
    return None

def calculate_spread(option1, option2):
    """
    Calculates the net cost and potential max profit for a spread strategy.
    """
    net_cost = option1['lastPrice'] - option2['lastPrice']
    max_profit = option2['strike'] - option1['strike'] - net_cost
    return net_cost, max_profit

def generate_spread_recommendation(ticker, option_type="call"):
    """
    Generates a recommendation for a bull call spread (for calls) or bear put spread (for puts).
    """
    stock_price, expirations = get_stock_data(ticker)

    for exp in expirations:
        calls, puts = get_options_data(ticker, exp)
        options = calls if option_type == "call" else puts

        filtered_options = filter_options(options, stock_price, option_type)

        if len(filtered_options) >= 2:
            spread_candidates = filtered_options.head(2)
            option1, option2 = spread_candidates.iloc[0], spread_candidates.iloc[1]
            net_cost, max_profit = calculate_spread(option1, option2)

            return (f"Recommended {option_type} spread: Buy {option1['strike']} Strike, "
                    f"Sell {option2['strike']} Strike, Net Cost: {net_cost}, Max Profit: {max_profit}")

    return f"No suitable {option_type} spreads found for {ticker}."

def generate_single_option_recommendation(ticker, option_type="call"):
    """
    Generates a buy recommendation for an individual options contract based on enhanced criteria.
    """
    stock_price, expirations = get_stock_data(ticker)

    recommendations = []
    for exp in expirations:
        calls, puts = get_options_data(ticker, exp)

        options = calls if option_type == "call" else puts
        filtered_options = filter_options(options, stock_price, option_type)

        best_option = select_option(filtered_options)
        if best_option is not None:
            recommendations.append((exp, best_option))

    if recommendations:
        exp, best_option = sorted(recommendations, key=lambda x: x[1]['impliedVolatility'])[0]
        return (f"Recommended {option_type} option: {ticker} {exp} {best_option['strike']} Strike Price "
                f"with Implied Volatility: {best_option['impliedVolatility']}")
    else:
        return f"No suitable {option_type} options found for {ticker}."

if __name__ == "__main__":
    tickers = ["AAPL", "TSLA", "AMZN", "GOOGL", "MSFT", "NVDA", "PYPL", "ADBE", "NFLX", "INTC", "CSCO", "CMCSA", "PEP", "COST", "TMUS", "AVGO", "TXN", "QCOM", "SBUX"]
    for ticker in tickers:
        recommendation = generate_single_option_recommendation(ticker, "put")
        print(recommendation)

    # ticker = input("Enter the stock ticker symbol: ").upper()
    # option_type = input("Enter option type (call/put): ").lower()
    # strategy_type = input("Enter strategy type (single/spread): ").lower()
    #
    # if strategy_type == "spread":
    #     recommendation = generate_spread_recommendation(ticker, option_type)
    # else:
    #     recommendation = generate_single_option_recommendation(ticker, option_type)
    #
    # print(recommendation)