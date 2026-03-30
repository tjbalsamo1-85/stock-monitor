from flask import Flask, render_template_string
import threading
import time
import yfinance as yf
from datetime import datetime

app = Flask(__name__)

# GLOBAL DATA STORAGE
stock_data = {}
last_check = None

TICKERS = ["AAPL", "TSLA", "MSFT"]

def check_stocks():
    global stock_data, last_check

    while True:
        print("Checking stocks...")

        new_data = {}

        for ticker in TICKERS:
            try:
                stock = yf.Ticker(ticker)
                price = stock.info.get("regularMarketPrice", "N/A")

                new_data[ticker] = {
                    "price": price,
                    "status": "OK"
                }

            except Exception as e:
                new_data[ticker] = {
                    "price": "Error",
                    "status": "Fail"
                }

        stock_data = new_data
        last_check = datetime.now().strftime("%H:%M:%S")

        print("Updated:", stock_data)

        time.sleep(30)


# START BACKGROUND THREAD
threading.Thread(target=check_stocks, daemon=True).start()


@app.route("/")
def dashboard():
    return render_template_string("""
    <h1>📈 Stock Dashboard</h1>
    <p><b>Last Check:</b> {{ last_check }}</p>

    <table border="1" cellpadding="8">
        <tr>
            <th>Ticker</th>
            <th>Price</th>
            <th>Status</th>
        </tr>

        {% for ticker, data in stocks.items() %}
        <tr>
            <td>{{ ticker }}</td>
            <td>{{ data.price }}</td>
            <td>{{ data.status }}</td>
        </tr>
        {% endfor %}
    </table>
    """, stocks=stock_data, last_check=last_check)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
