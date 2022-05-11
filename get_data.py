import requests_cache
from bs4 import BeautifulSoup
import re
from dateutil import parser

url = "https://www.frenchfilmfestival.co.nz/locations/Wellington"

watchlist = [
    "Another World",
    "Between Two Worlds",
    "Everything Went Fine",
    "Farewell, Mr. Haffmann",
    "La Traviata, My Brothers and I",
    "Love Songs for Tough Guys",
    "Madeleine Collins"
]

my_venues = [
    "Light House Cuba",
    "Embassy Theatre",
    "Light House Pauatahanui"
]

session = requests_cache.CachedSession('fff')

response = session.get(url)

soup = BeautifulSoup(response.text, features="html.parser")

venues = soup.find_all("div", attrs={"class": "venue-film-list"})

def get_sessions():
    sessions = []

    for venue in venues:
        for movie in venue.find_all("div", attrs={"class": "venue-film"}):
            venue_name = venue.find("h2").text
            title = movie.find("h3").find("a").text
            if title not in watchlist:
                continue
            if venue_name not in my_venues:
                continue
            for session in movie.find_all("p", attrs={"class": "sessionLine"}):
                session_date = re.search("(.+)\|(.+m)", session.text).group(1).strip()
                session_time = re.search("(.+)\|(.+m)", session.text).group(2).strip().replace(".", ":")
                link = session.a['href']
                time = parser.parse(f"{session_date} {session_time}")
                sessions.append({"name": title, "datetime": str(time), "venue": venue_name, "link": link})
    return sessions
            