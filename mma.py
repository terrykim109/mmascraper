import requests
import hashlib
import re
from bs4 import BeautifulSoup


def solve_challenge(session, url):
    response = session.get(url)
    match = re.search(r'var nonce="([^"]+)"', response.text)
    if not match:
        return
    
    nonce = match.group(1)
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
        
        if letter == "a":
            for row in rows[:1]:
                cols = row.select("td")
                for i, col in enumerate(cols):
                    print(f"col[{i}]: {col.text.strip()[:30]}")

        for row in rows:
            first = row.select_one("td:nth-child(1) a")
            last = row.select_one("td:nth-child(2) a")
            weight = row.select_one("td:nth-child(5)")
            slpm = row.select_one("td:nth-child(6)")
            str_acc = row.select_one("td:nth-child(7)")
            sapm = row.select_one("td:nth-child(8)")
            str_def = row.select_one("td:nth-child(9)")
            td_avg = row.select_one("td:nth-child(10)")
            td_acc = row.select_one("td:nth-child(11)")
            td_def = row.select_one("td:nth-child(12)")
            sub_avg = row.select_one("td:nth-child(13)")

            if not first or not last:
                continue

            name = f"{first.text.strip()} {last.text.strip()}"
            weight_val = weight.text.strip() if weight else "N/A"

            fighters.append({
                "name":         name,
                "link":         first["href"],
                "weight":       weight_val,
                "weight_class": get_weight_class(weight_val),
                "slpm":         slpm.text.strip() if slpm else "0",
                "str_acc":      str_acc.text.strip() if str_acc else "0",
                "sapm":         sapm.text.strip() if sapm else "0",
                "str_def":      str_def.text.strip() if str_def else "0",
                "td_avg":       td_avg.text.strip() if td_avg else "0",
                "td_acc":       td_acc.text.strip() if td_acc else "0",
                "td_def":       td_def.text.strip() if td_def else "0",
                "sub_avg":      sub_avg.text.strip() if sub_avg else "0",
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

        opponent_links = cols[1].select('a')
        opponent = opponent_links[1].text.strip() if len(opponent_links) > 1 else cols[1].text.strip()
       
        event_el = cols[6].select_one('a')
        fights.append({
            "result":   cols[0].text.strip(),
            "opponent": opponent,
            "event":    cols[6].text.strip(),
            "event_link": event_el['href'] if event_el else None,
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
    
def get_event_details(event_url):
    session = requests.Session()
    session.headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    solve_challenge(session, event_url)
    response = session.get(event_url)

    soup = BeautifulSoup(response.text, "html.parser")

    name = soup.select_one("span.b-content__title-highlight")
    name = name.text.strip() if name else "Unknown"

    # event details
    details = {}
    for item in soup.select("li.b-list__box-list-item"):
        label = item.select_one("i.b-list__box-item-title")
        if not label:
            continue
        key = label.text.strip().rstrip(":")
        val = item.text.replace(label.text, "").strip()
        if key:
            details[key] = val

    # all fights on the card
    fights = []
    for row in soup.select("tr.b-fight-details__table-row"):
        cols = row.select("td.b-fight-details__table-col")
        if len(cols) < 10:
            continue

        fighters = cols[1].select('a')
        fighter1 = fighters[0].text.strip() if len(fighters) > 0 else "N/A"
        fighter2 = fighters[1].text.strip() if len(fighters) > 1 else "N/A"

        fight_link = row.get("data-link")

        fights.append({
            "fighter1":  fighter1,
            "fighter2":  fighter2,
            "fight_link": fight_link,
            "method":    cols[7].text.strip(),
            "round":     cols[8].text.strip(),
            "time":      cols[9].text.strip(),
        })

    return {
        "name":    name,
        "date":    details.get("Date", "N/A"),
        "location": details.get("Location", "N/A"),
        "fights":  fights,
    }