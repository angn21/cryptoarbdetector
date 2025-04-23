import ccxt
import pandas as pd
import time
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import matplotlib.ticker as ticker
import os
from datetime import datetime

# Initialize the exchange clients
binance = ccxt.binance()
coinbase = ccxt.coinbase()
kraken = ccxt.kraken()
bitfinex = ccxt.bitfinex()
huobi = ccxt.huobi()  
kucoin = ccxt.kucoin()  

# Define the cryptocurrency pair (e.g., BTC/USDT)
symbol = 'BTC/USDT'

# Function to fetch price data from an exchange
def get_price(exchange, symbol):
    try:
        ticker = exchange.fetch_ticker(symbol)
        return ticker['last']  # Get the last price
    except Exception as e:
        print(f"Error fetching data from {exchange}: {e}")
        return None
    
# Fetch ticker with bid and ask for triangle calculations
def get_ticker(exchange, symbol):
    try:
        return exchange.fetch_ticker(symbol)
    except Exception as e:
        print(f"Error fetching ticker for {symbol} from {exchange.name}: {e}")
        return None

# Detect triangular arbitrage on a given exchange
def detect_triangular_arb(exchange, base='USDT'):
    symbols = ['BTC/USDT', 'ETH/USDT', 'ETH/BTC']
    tickers = {s: get_ticker(exchange, s) for s in symbols}

    if any(t is None for t in tickers.values()):
        return None  # skip if any ticker is missing

    try:
        start_amount = 1000  # Starting amount in USDT

        # Step 1: USDT → BTC
        usdt_to_btc = start_amount / tickers['BTC/USDT']['ask']  # use ask price to buy BTC

        # Step 2: BTC → ETH
        btc_to_eth = usdt_to_btc / tickers['ETH/BTC']['ask']  # use ask to buy ETH

        # Step 3: ETH → USDT
        eth_to_usdt = btc_to_eth * tickers['ETH/USDT']['bid']  # use bid to sell ETH

        profit = eth_to_usdt - start_amount
        profit_percent = (profit / start_amount) * 100  # Fixed logic here

        if profit > 0:
            return {
                'exchange': exchange.name,
                'start_amount': start_amount,
                'final_amount': eth_to_usdt,
                'profit': profit,
                'profit_percent': profit_percent,
                'path': 'USDT → BTC → ETH → USDT'
            }
        return None
    except Exception as e:
        print(f"Error during triangle calc on {exchange.name}: {e}")
        return None


# Collect price data in a pandas DataFrame
def fetch_arbitrage_opportunity():
    binance_price = get_price(binance, symbol)
    coinbase_price = get_price(coinbase, symbol)
    kraken_price = get_price(kraken, symbol)
    bitfinex_price = get_price(bitfinex, symbol)
    huobi_price = get_price(huobi, symbol)  # Get price from Huobi
    kucoin_price = get_price(kucoin, symbol)  # Get price from KuCoin

    if binance_price and coinbase_price and kraken_price and bitfinex_price and huobi_price and kucoin_price:
        # Calculate spread for each exchange compared to Binance
        spreads = {}
        spreads['Coinbase'] = (binance_price - coinbase_price) / coinbase_price * 100
        spreads['Kraken'] = (binance_price - kraken_price) / kraken_price * 100
        spreads['Bitfinex'] = (binance_price - bitfinex_price) / bitfinex_price * 100
        spreads['Huobi'] = (binance_price - huobi_price) / huobi_price * 100  # Spread for Huobi
        spreads['KuCoin'] = (binance_price - kucoin_price) / kucoin_price * 100  # Spread for KuCoin

        # Output the prices and spreads
        print(f"Binance: {binance_price} | Coinbase: {coinbase_price} | Kraken: {kraken_price} | Bitfinex: {bitfinex_price}")
        print(f"Huobi: {huobi_price} | KuCoin: {kucoin_price}")
        for exchange, spread in spreads.items():
            print(f"Spread with {exchange}: {spread:.2f}%")

        return {'timestamp': pd.Timestamp.now(), 'binance_price': binance_price, 'coinbase_price': coinbase_price, 'kraken_price': kraken_price, 'bitfinex_price': bitfinex_price, 'huobi_price': huobi_price, 'kucoin_price': kucoin_price, 'spreads': spreads}
    else:
        return None
    
# Initialize the data storage
data = []

# Initialize the plot
plt.figure(figsize=(12, 6))
ax = plt.gca()
# Secondary Y-axis for actual price data
ax2 = ax.twinx()
line_price = ax2.plot([], [], color='grey', linestyle='--', label='Binance Price')[0]

# Format second y-axis (price)
ax2.set_ylabel('Binance Price (USDT)', color='grey')
ax2.tick_params(axis='y', labelcolor='grey')
ax.set_title('Crypto Arbitrage Spread Over Time')
ax.set_xlabel('Timestamp')
ax.set_ylabel('Spread (%)')

# Create line objects for each exchange
line_coinbase, = ax.plot([], [], marker='o', linestyle='-', color='b', label="Spread with Coinbase")
line_kraken, = ax.plot([], [], marker='x', linestyle='-', color='g', label="Spread with Kraken")
line_bitfinex, = ax.plot([], [], marker='^', linestyle='-', color='r', label="Spread with Bitfinex")
line_huobi, = ax.plot([], [], marker='s', linestyle='-', color='orange', label="Spread with Huobi")
line_kucoin, = ax.plot([], [], marker='D', linestyle='-', color='brown', label="Spread with KuCoin")

# Add gridlines for better visualization
ax.grid(True, which='both', linestyle='--', linewidth=0.5)

# Set x-ticks to be empty for now (this will be dynamically updated)
ax.set_xticklabels([])

# Set up legend
lines = [line_coinbase, line_kraken, line_bitfinex, line_huobi, line_kucoin, line_price]
labels = [line.get_label() for line in lines]
ax.legend(lines, labels, loc='upper left')

# Set the CSV directory
csv_folder = "C:/Users/Anmol/Desktop/python stuff/learning coding again/crypto arb detector"
session_timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
csv_filename = f"arbitrage_data_{session_timestamp}.csv"

# Function to save data to CSV
def save_data_to_csv(data, filename="arbitrage_data.csv"):
    filepath = os.path.join(csv_folder, filename)

    # Convert the data list into a DataFrame
    if data:
        df = pd.DataFrame(data)

        # Ensure the 'timestamp' column is a datetime object
        df['timestamp'] = pd.to_datetime(df['timestamp'])

        # Save to CSV (append if exists, write header if new)
        df.to_csv(filepath, index=False, mode='a', header=not os.path.exists(filepath))

# Function to update the plot
def update_plot(frame):
    opportunity = fetch_arbitrage_opportunity()
    if opportunity:
        data.append(opportunity)
        df = pd.DataFrame(data)
        
        # Save data to CSV
        save_data_to_csv(data)

        # Update price line on secondary y-axis
        binance_prices = df['binance_price']
        line_price.set_data(df['timestamp'], binance_prices)

        # Adjust the Binance price y-axis (secondary axis) range
        if len(binance_prices) > 1:  # Ensure there's more than one data point
            min_price = binance_prices.min()
            max_price = binance_prices.max()
            price_range = max_price - min_price

            # Set a minimum range if the price variation is too small
            if price_range < 100:  # Adjust this threshold based on the data you're working with
                padding = 50  # Add a fixed padding if the range is too small
            else:
                padding = price_range * 0.01  # Add 1% padding based on the price range

            # Apply the padding to create a visible difference
            ax2.set_ylim(min_price - padding, max_price + padding)
        else:
            # Set a default range for the y-axis when there’s not enough data
            ax2.set_ylim(20000, 70000)  # Example range for BTC (adjust if needed)

        # Update the plot data for each exchange (including Huobi and KuCoin)
        line_coinbase.set_data(df['timestamp'], df['spreads'].apply(lambda x: x['Coinbase']))
        line_kraken.set_data(df['timestamp'], df['spreads'].apply(lambda x: x['Kraken']))
        line_bitfinex.set_data(df['timestamp'], df['spreads'].apply(lambda x: x['Bitfinex']))
        line_huobi.set_data(df['timestamp'], df['spreads'].apply(lambda x: x['Huobi']))
        line_kucoin.set_data(df['timestamp'], df['spreads'].apply(lambda x: x['KuCoin']))

        # Update x-axis labels for each frame (timestamp formatting)
        ax.set_xticks(df['timestamp'])
        ax.set_xticklabels(df['timestamp'].dt.strftime('%H:%M:%S'), rotation=45)

        # Adjust x-axis limits dynamically based on data
        ax.set_xlim(df['timestamp'].min(), df['timestamp'].max())

        # Set y-axis limits for spread (primary axis) with dynamic padding
        min_spread = min(df['spreads'].apply(lambda x: min(x.values())))
        max_spread = max(df['spreads'].apply(lambda x: max(x.values())))

        # If the spread range is very small, apply a default padding
        if max_spread - min_spread < 0.1:  # If spread is too narrow
            padding = 0.1  # Set a minimum range for the spread axis
        else:
            padding = (max_spread - min_spread) * 0.1  # Add 10% padding for spread axis

        # Set dynamic y-limits for spread with padding
        ax.set_ylim(min_spread - padding, max_spread + padding)

        # Adjust spread y-ticks
        ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=False, prune='both', nbins=6))
        ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'{x:.2f}%'))
    
    # Triangular arbitrage detection
    for ex in [binance, kucoin, bitfinex]:
        triangle = detect_triangular_arb(ex)
    if triangle:
        print(f"[Triangular Arb] {triangle['exchange']}: {triangle['profit_percent']:.3f}% via {triangle['path']}")
        # Optionally save to CSV
        triangle_log = {
            'timestamp': pd.Timestamp.now(),
            'exchange': triangle['exchange'],
            'path': triangle['path'],
            'profit_percent': triangle['profit_percent'],
            'final_amount': triangle['final_amount']
        }
        pd.DataFrame([triangle_log]).to_csv(
            os.path.join(csv_folder, 'triangular_arbs.csv'), mode='a', header=not os.path.exists(os.path.join(csv_folder, 'triangular_arbs.csv')), index=False
        )


    return line_coinbase, line_kraken, line_bitfinex, line_huobi, line_kucoin, line_price

# Set up the animation
ani = FuncAnimation(plt.gcf(), update_plot, frames=range(50), interval=5000, repeat=False)

# Display the plot
plt.tight_layout()
plt.show()
