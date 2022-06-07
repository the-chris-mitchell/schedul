from datetime import datetime, timedelta
from clients import get_cached_soup

from models import Film, Session, Venue

BASE_URL = "https://www.nziff.co.nz"
URL = BASE_URL + "/nziff-2022/2022/films/title/"



def get_sessions() -> list[Session]:
    sessions: list[Session] = []

    soup = get_cached_soup(URL, "nziff")
    film_cards =  soup.find_all("article", class_="film-card")

    for film_card in film_cards:
        title = film_card.find("span", itemprop="name").text
        url = film_card.a.get("href")

        film_html = get_cached_soup(BASE_URL + url, "nziff")

        minutes = film_html.find("span", itemprop="duration").text.split(" ")[0]

        duration_delta = timedelta(minutes=int(minutes))

        film = Film(title, duration_delta)

        session = Session(film, Venue("Venue"), datetime.now(), "http://google.com")

        sessions.append(session)

    return(sessions)