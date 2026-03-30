import yfinance as yf
import time
from datetime import datetime

alerted = {}

targets = {
    "AAPL": {"upper": 400, "lower": 200},
    "MSFT": {"upper": 400, "lower": 300},
    "GOOG": {"upper": 350, "lower": 200},
    "NVDA": {"upper": 180, "lower": 120},
    "TSLA": {"upper": 400, "lower": 250}
}

while True:
    now = datetime.now()
    weekday = now.weekday()

    print(f"\n⏰ {now.strftime('%Y-%m-%d %H:%M:%S')}")

    if weekday < 5:
        print("Running check...")

        for ticker, levels in targets.items():
            print("Checking:", ticker)

            stock = yf.Ticker(ticker)

            try:
                data = stock.history(period="5d")
            except Exception as e:
                print(f"{ticker}: ERROR - {e}")
                continue

            if data.empty:
                print(f"{ticker}: ❌ No data")
                continue

            price = data["Close"].iloc[-1]

            print(f"{ticker}: ${price:.2f} | Range: {levels['lower']} - {levels['upper']}")

            if ticker not in alerted:
                alerted[ticker] = None

            if price > levels["upper"] and alerted[ticker] != "upper":
                print(f"🚨 {ticker} ABOVE {levels['upper']}")
                alerted[ticker] = "upper"

            elif price < levels["lower"] and alerted[ticker] != "lower":
                print(f"📉 {ticker} BELOW {levels['lower']}")
                alerted[ticker] = "lower"

            else:
                if levels["lower"] < price < levels["upper"]:
                    alerted[ticker] = None

    else:
        print("Weekend — skipping checks")

    print("----- next check in 30 minutes -----")
    time.sleep(1800)
