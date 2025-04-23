import ccxt
import pandas as pd
import time

# Initialize the exchange clients
binance = ccxt.binance()
coinbase = ccxt.coinbase()

# Define the cryptocurrency pair (e.g., BTC/USD)
symbol = 'BTC/USDT'

# Function to fetch price data from an exchange
def get_price(exchange, symbol):
    try:
        ticker = exchange.fetch_ticker(symbol)
        return ticker['last']  # Get the last price
    except Exception as e:
        print(f"Error fetching data from {exchange}: {e}")
        return None

# Collect price data in a pandas DataFrame
def fetch_arbitrage_opportunity():
    binance_price = get_price(binance, symbol)
    coinbase_price = get_price(coinbase, symbol)

    if binance_price and coinbase_price:
        spread = (binance_price - coinbase_price) / coinbase_price * 100  # Spread in percentage
        print(f"Binance: {binance_price} | Coinbase: {coinbase_price} | Spread: {spread:.2f}%")
        return {'timestamp': pd.Timestamp.now(), 'binance_price': binance_price, 'coinbase_price': coinbase_price, 'spread': spread}
    else:
        return None

# Running the arbitrage detector and collecting data every 5 seconds
data = []
for _ in range(10):  # Run this 10 times (you can adjust as needed)
    opportunity = fetch_arbitrage_opportunity()
    if opportunity:
        data.append(opportunity)
    time.sleep(5)  # Delay between fetches (5 seconds)

# Convert the data into a DataFrame
df = pd.DataFrame(data)
print(df)
