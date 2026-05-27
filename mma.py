import requests
import hashlib
import re
from bs4 import BeautifulSoup


def solve_challenge(session, url):
    response = session.get(url)
    nonce = re.search(r'var nonce="([^"]+)"', response.text).group(1)
    n = 0

    while True:
        hash_val = hashlib.sha256(f"{nonce}:{n}".encode()).hexdigest()
        if hash_val.startswith("00"):
            break
        n += 1

    session.post("http://ufcstats.com/__c", data={"nonce": nonce, "n": n})


def get_fighter_image(name):
    try:
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{name.replace(' ', '_')}"
        response = requests.get(url, timeout=5)
        data = response.json()
        if "thumbnail" in data:
            return data["thumbnail"]["source"]
        return None
    except:
        return None


def get_weight_class(weight_str):
    try:
        lbs = int(weight_str.replace("lbs.", "").strip())
    except:
        return "Unknown"

    if lbs <= 115:
        return "Women's Strawweight"
    elif lbs <= 125:
        return "Flyweight"
    elif lbs <= 135:
        return "Bantamweight"
    elif lbs <= 145:
        return "Featherweight"
    elif lbs <= 155:
        return "Lightweight"
    elif lbs <= 170:
        return "Welterweight"
    elif lbs <= 185:
        return "Middleweight"
    elif lbs <= 205:
        return "Light Heavyweight"
    else:
        return "Heavyweight"


def get_fighters_stats():
    fighters = []
    session = requests.Session()
    session.headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"

    for letter in "abcdefghijklmnopqrstuvwxyz":
        url = f"http://ufcstats.com/statistics/fighters?char={letter}&page=all"
        solve_challenge(session, url)
        response = session.get(url)

        soup = BeautifulSoup(response.text, "html.parser")
        rows = soup.select("tr.b-statistics__table-row")

        for row in rows:
            first = row.select_one("td:nth-child(1) a")
            last = row.select_one("td:nth-child(2) a")
            weight = row.select_one("td:nth-child(5)")

            if not first or not last:
                continue

            name = f"{first.text.strip()} {last.text.strip()}"
            weight_val = weight.text.strip() if weight else "N/A"

            fighters.append({
                "name": name,
                "link": first["href"],
                "weight": weight_val,
                "weight_class": get_weight_class(weight_val)
            })

        print(f"{letter.upper()}: {len(rows)} fighters scraped")

    return fighters


def get_fighter_details(fighter_url):
    session = requests.Session()
    session.headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    solve_challenge(session, fighter_url)
    response = session.get(fighter_url)

    soup = BeautifulSoup(response.text, "html.parser")

    name = soup.select_one("span.b-content__title-highlight").text.strip()
    record = soup.select_one("span.b-content__title-record").text.strip()
    nickname = soup.select_one("p.b-content__Nickname")
    nickname = nickname.text.strip() if nickname else ""

    # parse stats into a dict 
    stats = {}
    for item in soup.select("li.b-list__box-list-item"):
        label = item.select_one("i.b-list__box-item-title")
        if not label:
            continue
        key = label.text.strip().rstrip(":")
        val = item.text.replace(label.text, "").strip()
        if key:
            stats[key] = val

    fights = []
    for row in soup.select("tr.b-fight-details__table-row"):
        cols = row.select("td.b-fight-details__table-col")
        if len(cols) < 10:
            continue
        fights.append({
            "result":   cols[0].text.strip(),
            "opponent": cols[1].text.strip(),
            "event":    cols[2].text.strip(),
            "method":   cols[7].text.strip(),
            "round":    cols[8].text.strip(),
            "time":     cols[9].text.strip(),
        })

    return {
        "Name":      name,
        "Nickname":  nickname,
        "Record":    record,
        "Height":    stats.get("Height", "N/A"),
        "Weight":    stats.get("Weight", "N/A"),
        "Reach":     stats.get("Reach", "N/A"),
        "Stance":    stats.get("Stance", "N/A"),
        "DOB":       stats.get("DOB", "N/A"),
        "SLpM":      stats.get("SLpM", "N/A"),
        "Str. Acc.": stats.get("Str. Acc.", "N/A"),
        "SApM":      stats.get("SApM", "N/A"),
        "Str. Def.": stats.get("Str. Def.", "N/A"),
        "TD Avg.":   stats.get("TD Avg.", "N/A"),
        "TD Acc.":   stats.get("TD Acc.", "N/A"),
        "TD Def.":   stats.get("TD Def.", "N/A"),
        "Sub. Avg.": stats.get("Sub. Avg.", "N/A"),
        "Fights":    fights,
        "Image":     get_fighter_image(name),
    }