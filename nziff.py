from datetime import datetime, timedelta
from bs4 import BeautifulSoup # type: ignore
import requests_cache

from models import Film, Session, Venue

BASE_URL = "https://www.nziff.co.nz"
URL = BASE_URL + "/nziff-2022/2022/films/title/"

def get_soup(url: str, cache: str):
    requests_session = requests_cache.CachedSession(cache)

    response = requests_session.get(url)

    return BeautifulSoup(response.text, features="html.parser")

def get_sessions() -> list[Session]:
    sessions: list[Session] = []

    soup = get_soup(URL, "nziff")
    film_cards =  soup.find_all("article", class_="film-card")

    for film_card in film_cards:
        title = film_card.find("span", itemprop="name").text
        url = film_card.a.get("href")

        film_html = get_soup(BASE_URL + url, "nziff")

        minutes = film_html.find("span", itemprop="duration").text.split(" ")[0]

        duration_delta = timedelta(minutes=int(minutes))

        film = Film(title, duration_delta)

        session = Session(film, Venue("Venue"), datetime.now(), "http://google.com")

        sessions.append(session)

    return(sessions)