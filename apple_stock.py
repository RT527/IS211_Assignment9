# Rafi Talukder Assignment_9
# URL scraped (data source): https://query1.finance.yahoo.com/v8/finance/chart/AAPL?
"""---------------------------------------------------------------------------------"""
# This avoids HTML 404s by requesting structured JSON instead, then parsing it in Python.
"""---------------------------------------------------------------------------------"""
import requests
from datetime import datetime, timezone
ENDPOINTS = [
    ("https://query1.finance.yahoo.com/v8/finance/chart/AAPL", {"interval": "1d", "range": "1mo"}),
    ("https://query2.finance.yahoo.com/v8/finance/chart/AAPL", {"interval": "1d", "range": "3mo"}),
]
REQ_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json,text/plain,*/*",
    "Accept-Language": "en-US,en;q=0.9",
}
"""---------------------------------------------------------------------------------"""
def get_chart_json(): #This fetches the JSON
    last_error = None
    for url, params in ENDPOINTS:
        try:
            resp = requests.get(url, params=params, headers=REQ_HEADERS, timeout=20)
            resp.raise_for_status()
            payload = resp.json()
            if payload.get("chart", {}).get("result"):
                return payload
        except Exception as e:
            last_error = e
            continue
    raise last_error # This is to bubble up last error if both fail.
"""---------------------------------------------------------------------------------"""
def make_rows(payload): # This parses JSON
    result = payload["chart"]["result"][0]
    stamps = result.get("timestamp", []) or []
    closes = result["indicators"]["quote"][0].get("close", []) or []
    rows = []
    for ts, close_val in zip(stamps, closes):
        if close_val is None:
            continue
        day = datetime.fromtimestamp(ts, tz=timezone.utc).date().isoformat()
        rows.append((day, close_val))
    return rows
"""---------------------------------------------------------------------------------"""
def show(rows): # Display the output in a clean table style.
    print("""---------------------------------------------------------------------------------""")
    print("This is the AAPL Historical Prices — Date vs Close")
    print("""---------------------------------------------------------------------------------""")
    for day, close_price in rows:
        print(f"{day}\t{close_price}")
    print("""---------------------------------------------------------------------------------""")
    print(f"Total records: {len(rows)}")
    if not rows:
        print("There is no data found, API format may have changed or been deleted.")
"""---------------------------------------------------------------------------------"""
def main():
    data = get_chart_json()
    rows = make_rows(data)
    show(rows)
"""---------------------------------------------------------------------------------"""
if __name__ == "__main__":
    print("Running apple scraper...")
    main()