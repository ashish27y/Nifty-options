# app.py

from flask import Flask, request, jsonify
from utils.fyers_config import get_fyers
import datetime
import math
import pytz

app = Flask(__name__)
fyers = get_fyers()

NIFTY_LOT_SIZE = 50

def get_current_nifty_price():
    data = fyers.quotes({"symbols": "NSE:NIFTY50-INDEX"})
    return data['d'][0]['v']['lp']

def get_weekly_expiry():
    today = datetime.datetime.now(pytz.timezone("Asia/Kolkata"))
    days_ahead = 4 - today.weekday()
    if days_ahead < 0:
        days_ahead += 7
    expiry_date = today + datetime.timedelta(days=days_ahead)
    return expiry_date.strftime("%y%m%d")  # YYMMDD

def get_option_symbol(option_type):
    spot_price = get_current_nifty_price()
    strike = int(round(spot_price / 50) * 50)
    expiry = get_weekly_expiry()
    symbol = f"NSE:NIFTY{expiry}{strike}{option_type}"
    return symbol

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    signal = data.get("signal")

    if signal not in ["BUY", "SELL", "EXIT"]:
        return jsonify({"error": "Invalid signal"}), 400

    if signal == "EXIT":
        positions = fyers.positions()
        for pos in positions["netPositions"]:
            if "NIFTY" in pos["symbol"]:
                qty = int(pos["netQty"])
                if qty != 0:
                    side = -1 if qty > 0 else 1
                    fyers.place_order({
                        "symbol": pos["symbol"],
                        "qty": abs(qty),
                        "type": 2,
                        "side": side,
                        "productType": "INTRADAY",
                        "limitPrice": 0,
                        "stopPrice": 0,
                        "validity": "DAY",
                        "disclosedQty": 0,
                        "offlineOrder": False,
                        "orderType": "MARKET"
                    })
        return jsonify({"status": "Exit order placed"})

    option_type = "CE" if signal == "BUY" else "PE"
    symbol = get_option_symbol(option_type)

    order = {
        "symbol": symbol,
        "qty": NIFTY_LOT_SIZE,
        "type": 2,
        "side": 1,
        "productType": "INTRADAY",
        "limitPrice": 0,
        "stopPrice": 0,
        "validity": "DAY",
        "disclosedQty": 0,
        "offlineOrder": False,
        "orderType": "MARKET"
    }

    res = fyers.place_order(order)
    return jsonify(res)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
  
