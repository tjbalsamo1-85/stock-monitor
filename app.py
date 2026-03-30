import yfinance as yf
import time
import threading
import os
from datetime import datetime
import pytz
from flask import Flask, jsonify, render_template_string

app = Flask(__name__)

alerted = {}
latest_data = {}
last_check = "Never"

targets = {
    "AAPL": {"upper": 400, "lower": 200},
    "MSFT": {"upper": 400, "lower": 300},
    "GOOG": {"upper": 350, "lower": 200},
    "NVDA": {"upper": 180, "lower": 120},
    "TSLA": {"upper": 400, "lower": 250}
}

est = pytz.timezone("US/Eastern")


def check_stocks():
    global last_check, latest_data

    while True:
        now_est = datetime.now(est)

        if now_est.weekday() < 5 and (9 <= now_est.hour < 16 or (now_est.hour == 9 and now_est.minute >= 30)):
            print(f"⏰ Checking at {now_est}")

            for ticker, levels in targets.items():
                try:
                    stock = yf.Ticker(ticker)
                    data = stock.history(period="1d")

                    if data.empty:
                        continue

                    price = float(data["Close"].iloc[-1])

                    status = "IN RANGE"
                    if ticker not in alerted:
                        alerted[ticker] = None

                    if price > levels["upper"] and alerted[ticker] != "upper":
                        status = "ABOVE 🚨"
                        alerted[ticker] = "upper"

                    elif price < levels["lower"] and alerted[ticker] != "lower":
                        status = "BELOW 📉"
                        alerted[ticker] = "lower"

                    elif levels["lower"] < price < levels["upper"]:
                        alerted[ticker] = None

                    latest_data[ticker] = {
                        "price": round(price, 2),
                        "upper": levels["upper"],
                        "lower": levels["lower"],
                        "status": status
                    }

                except Exception as e:
                    print(f"{ticker} error: {e}")

            last_check = now_est.strftime("%Y-%m-%d %H:%M:%S")

        else:
            print("Market closed")

        time.sleep(1800)


@app.route("/data")
def data():
    return jsonify({
        "last_check": last_check,
        "stocks": latest_data
    })


@app.route("/")
def home():
    return render_template_string("""
    <html>
    <head>
        <title>Stock Dashboard</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    </head>
    <body style="font-family: Arial; padding:20px;">

        <h1>📈 Stock Dashboard</h1>
        <p id="lastCheck">Loading...</p>

        <table border="1" cellpadding="10">
            <thead>
                <tr>
                    <th>Ticker</th>
                    <th>Price</th>
                    <th>Range</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody id="tableBody"></tbody>
        </table>

        <h2>📊 Chart (AAPL)</h2>
        <canvas id="chart" width="600" height="300"></canvas>

        <script>
            let chart;

            async function loadData() {
                const res = await fetch('/data');
                const data = await res.json();

                document.getElementById("lastCheck").innerText =
                    "Last Check: " + data.last_check;

                let rows = "";

                for (let ticker in data.stocks) {
                    let s = data.stocks[ticker];

                    let color = "black";
                    if (s.status.includes("ABOVE")) color = "red";
                    else if (s.status.includes("BELOW")) color = "orange";
                    else color = "green";

                    rows += `
                        <tr>
                            <td>${ticker}</td>
                            <td>${s.price}</td>
                            <td>${s.lower} - ${s.upper}</td>
                            <td style="color:${color}">${s.status}</td>
                        </tr>
                    `;
                }

                document.getElementById("tableBody").innerHTML = rows;
            }

            async function loadChart() {
                const res = await fetch("https://query1.finance.yahoo.com/v8/finance/chart/AAPL?range=1d&interval=5m");
                const data = await res.json();

                const prices = data.chart.result[0].indicators.quote[0].close;
                const labels = prices.map((_, i) => i);

                if (chart) chart.destroy();

                chart = new Chart(document.getElementById("chart"), {
                    type: "line",
                    data: {
                        labels: labels,
                        datasets: [{
                            label: "AAPL",
                            data: prices
                        }]
                    }
                });
            }

            async function refresh() {
                await loadData();
                await loadChart();
            }

            refresh();
            setInterval(refresh, 30000);
        </script>

    </body>
    </html>
    """)


if __name__ == "__main__":
    thread = threading.Thread(target=check_stocks)
    thread.daemon = True
    thread.start()

    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)




