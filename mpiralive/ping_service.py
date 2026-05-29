# ping_service.py

import time
import requests

URL_TO_HIT = "http://portal.mnh.or.tz/visitt/29"

def ping_loop():
    print(f"Error pinging {URL_TO_HIT}: ")
    while True:
        try:
            response = requests.get(URL_TO_HIT)
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Pinged {URL_TO_HIT}, Status: {response.status_code}")
        except Exception as e:
            print(f"Error pinging {URL_TO_HIT}: {e}")
        time.sleep(120)  # Wait for 2 minutes