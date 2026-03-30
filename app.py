import yfinance as yf
import time
import threading
import os
from datetime import datetime
import pytz
from flask import Flask

app = Flask(__name__)

# Track alert state
alerted = {}

# Store latest data for web display
latest_data = {}
last_check = "Never"

# Stock targets
targets = {
    "AAPL": {"upper": 400, "lower": 200},
    "MSFT": {"upper": 400, "lower": 300},
    "GOOG": {"upper": 350, "lower": 200},
    "NVDA": {"upper": 180, "lower": 120},
    "TSLA": {"upper": 400, "lower": 250}
}

# Timezone (US market)
est = pytz.timezone("US/Eastern")


def check_stocks():
    global last_check, latest_data

    while True:
        now_est = datetime.now(est)
        weekday = now_est.weekday()

        print(f"\n⏰ {now_est}")

        # Only run Mon–Fri, 9:30–16:00 EST
        if weekday < 5 and (9 <= now_est.hour < 16 or (now_est.hour == 9 and now_est.minute >= 30)):
            print("Market open — checking stocks")

            for ticker, levels in targets.items():
                try:
                    stock = yf.Ticker(ticker)
                    data = stock.history(period="1d")

                    if data.empty:
                        print(f"{ticker}: ❌ No data")
                        continue

                    price = data["Close"].iloc[-1]

                    latest_data[ticker] = {
                        "price": round(price, 2),
                        "upper": levels["upper"],
                        "lower": levels["lower"],
                        "status": "IN RANGE"
                    }

                    print(f"{ticker}: {price}")

                    if ticker not in alerted:
                        alerted[ticker] = None

                    if price > levels["upper"] and alerted[ticker] != "upper":
                        print(f"🚨 {ticker} ABOVE {levels['upper']}")
                        alerted[ticker] = "upper"
                        latest_data[ticker]["status"] = "ABOVE 🚨"

                    elif price < levels["lower"] and alerted[ticker] != "lower":
                        print(f"📉 {ticker} BELOW {levels['lower']}")
                        alerted[ticker] = "lower"
                        latest_data[ticker]["status"] = "BELOW 📉"

                    else:
                        if levels["lower"] < price < levels["upper"]:
                            alerted[ticker] = None
                            latest_data[ticker]["status"] = "IN RANGE"

                except Exception as e:
                    print(f"{ticker}: ERROR - {e}")

            last_check = now_est.strftime("%Y-%m-%d %H:%M:%S")

        else:
            print("Market closed — skipping")

        print("----- next check in 30 minutes -----")
        time.sleep(1800)


@app.route("/")
def home():
    html = f"<h1>📈 Stock Monitor</h1>"
    html += f"<p>Last Check (EST): {last_check}</p>"
    html += "<table border='1' cellpadding='10'><tr><th>Ticker</th><th>Price</th><th>Range</th><th>Status</th></tr>"

    for ticker, data in latest_data.items():
        color = "black"
        if "ABOVE" in data["status"]:
            color = "red"
        elif "BELOW" in data["status"]:
            color = "orange"
        elif "IN RANGE" in data["status"]:
            color = "green"

        html += f"""
        <tr>
            <td>{ticker}</td>
            <td>{data['price']}</td>
            <td>{data['lower']} - {data['upper']}</td>
            <td style='color:{color}'>{data['status']}</td>
        </tr>
        """

    html += "</table>"
    return html


if __name__ == "__main__":
    # Start background thread
    thread = threading.Thread(target=check_stocks)
    thread.daemon = True
    thread.start()

    # Run Flask app
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)


