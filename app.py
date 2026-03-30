from flask import Flask, render_template_string
import yfinance as yf

app = Flask(__name__)

targets = {
    "AAPL": {"upper": 400, "lower": 200},
    "MSFT": {"upper": 400, "lower": 300},
    "GOOG": {"upper": 350, "lower": 200},
    "NVDA": {"upper": 180, "lower": 120},
    "TSLA": {"upper": 400, "lower": 250}
}

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Stock Monitor</title>
    <style>
        body { font-family: Arial; background: #111; color: #fff; }
        table { border-collapse: collapse; width: 60%; margin: auto; }
        th, td { padding: 10px; text-align: center; }
        th { background: #333; }
        tr:nth-child(even) { background: #222; }
        .green { color: #00ff88; }
        .red { color: #ff4d4d; }
        .yellow { color: #ffd700; }
    </style>
</head>
<body>
    <h1 style="text-align:center;">📈 Stock Monitor</h1>
    <table border="1">
        <tr>
            <th>Ticker</th>
            <th>Price</th>
            <th>Range</th>
            <th>Status</th>
        </tr>
        {% for stock in stocks %}
        <tr>
            <td>{{ stock.ticker }}</td>
            <td>{{ stock.price }}</td>
            <td>{{ stock.lower }} - {{ stock.upper }}</td>
            <td class="{{ stock.color }}">{{ stock.status }}</td>
        </tr>
        {% endfor %}
    </table>
</body>
</html>
"""

@app.route("/")
def home():
    stocks_data = []

    for ticker, levels in targets.items():
        stock = yf.Ticker(ticker)
        data = stock.history(period="1d")

        if data.empty:
            continue

        price = round(data["Close"].iloc[-1], 2)

        if price > levels["upper"]:
            status = "ABOVE"
            color = "green"
        elif price < levels["lower"]:
            status = "BELOW"
            color = "red"
        else:
            status = "IN RANGE"
            color = "yellow"

        stocks_data.append({
            "ticker": ticker,
            "price": price,
            "upper": levels["upper"],
            "lower": levels["lower"],
            "status": status,
            "color": color
        })

    return render_template_string(HTML, stocks=stocks_data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

