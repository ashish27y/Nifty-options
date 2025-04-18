# utils/fyers_config.py

from fyers_apiv3 import fyersModel

def get_fyers():
    access_token = "QWTX66I4I6"
    client_id = "TUA7KDAVI1-100"
    fyers = fyersModel.FyersModel(client_id=client_id, token=access_token, log_path="/tmp/")
    return fyers
  
