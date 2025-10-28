# Rafi Talukder Assignment_9
# URL scraped: https://www.cbssports.com/nfl/stats/player/rushing/nfl/regular/qualifiers/
"""---------------------------------------------------------------------------------"""
import sys
import re
import requests
from bs4 import BeautifulSoup
"""---------------------------------------------------------------------------------"""
URL = "https://www.cbssports.com/nfl/stats/player/rushing/nfl/regular/qualifiers/" # This defines  the target URL and HTTP headers
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}
"""---------------------------------------------------------------------------------"""
def fetch_html(url: str) -> str: # This is the HTTP Request, fetches the HTML from CBS
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print("Error fetching the webpage:", e, file=sys.stderr)
        sys.exit(1)
"""---------------------------------------------------------------------------------"""
def parse_rushing_stats(html: str): # This parses the HTML table using beautiful soup
    """Extract rushing touchdown data from the CBS stats table."""
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table") # This finds the table that has a players stats
    if not table:
        raise RuntimeError("Could not find a stats table on the page.")
    headers = [th.get_text(strip=True) for th in table.find("thead").find_all("th")]
    lower_headers = [h.lower() for h in headers]
    # This is to identify column positions
    idx_player = next((i for i, h in enumerate(lower_headers) if "player" in h), None)
    idx_pos = next((i for i, h in enumerate(lower_headers) if h in ("pos", "position")), None)
    idx_team = next((i for i, h in enumerate(lower_headers) if h in ("team", "tm")), None)
    idx_td = next((i for i, h in enumerate(lower_headers)
                   if "td" in h and "yd" not in h and "att" not in h), None)

    if idx_player is None or idx_td is None:
        raise RuntimeError("Could not find the required Player or TD columns.")
    players = [] # This extracts player data
    tbody = table.find("tbody")
    for tr in tbody.find_all("tr"):
        cells = tr.find_all("td")
        if len(cells) < max(idx_player, idx_td) + 1:
            continue

        def cell_text(i):
            return cells[i].get_text(strip=True) if i is not None and i < len(cells) else ""

        player = cell_text(idx_player)
        pos = cell_text(idx_pos)
        team = cell_text(idx_team)
        td_text = cell_text(idx_td)
        match = re.search(r"\d+", td_text)
        td_num = match.group(0) if match else "0"

        if player:
            players.append({
                "player": player,
                "pos": pos or "N/A",
                "team": team or "N/A",
                "td": td_num
            })
    return players
"""---------------------------------------------------------------------------------"""
def main(): # This will display the top 20 players
    html = fetch_html(URL)
    try:
        rushing_data = parse_rushing_stats(html)
    except Exception as e:
        print("Error parsing stats:", e, file=sys.stderr)
        sys.exit(2)
    if not rushing_data:
        print("No rushing data found.", file=sys.stderr)
        sys.exit(2)

    print("""---------------------------------------------------------------------------------""")
    print("NFL Rushing Leaders — Touchdowns (Top 20)")
    print(f"Source: {URL}")
    print("""---------------------------------------------------------------------------------""")
    for i, player in enumerate(rushing_data[:20], start=1):
        print(f"{i:>2}. {player['player']} ({player['pos']} - {player['team']}) — TDs: {player['td']}")
    print("""---------------------------------------------------------------------------------""")
    print(f"Total records found: {len(rushing_data)}")
"""---------------------------------------------------------------------------------"""
if __name__ == "__main__":
    print("Running football scraper...")
    main()