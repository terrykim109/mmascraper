import requests
from bs4 import BeautifulSoup

# Scraping Fighter Statistics from UFC Stats website.
def get_fighters_stats():
    url = "http://ufcstats.com/statistics/fighters"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    rowsTable = soup.select('tr.b-statistics__table-row')
    fighters = []

    for row in rowsTable:
        name_link = row.select_one('td.b-statistics__table-col:nth-child(2) a')
     
        if name_link:
            name = name_link.text.strip()
            link = name_link['href']
            fighters.append({'name': name, 'link': link})

    return fighters

def get_fighter_details(fighter_url):
    response = requests.get(fighter_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    name = soup.select_one('span.b-content__title-highlight').text.strip()
    stats = {
        'Name': name,
        'Height': soup.find(text="Height:").find_next().text.strip(),
        'Weight': soup.find(text="Weight:").find_next().text.strip(),
        'Reach': soup.find(text="Reach:").find_next().text.strip(),
        'Stance': soup.find(text="Stance:").find_next().text.strip(),
        'DOB': soup.find(text="DOB:").find_next().text.strip(),
    }
    return stats


