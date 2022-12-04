from datetime import timedelta

import arrow  # type: ignore
from clients.soup import get_cached_soup
from models.festival import Festival
from models.film import Film
from models.session import Session
from models.venue import Venue

BASE_URL = "https://www.nziff.co.nz"
URL = f"{BASE_URL}/nziff-2022/wellington/films/title/"


class NZInternationalFilmFestival(Festival):
    @property
    def full_name(self) -> str:
        return "Whānau Mārama: New Zealand International Film Festival"

    @property
    def short_name(self) -> str:
        return "nziff"

    def get_sessions(self) -> None:
        sessions: list[Session] = []

        soup = get_cached_soup(URL, "nziff")
        film_cards =  soup.find_all("article", class_="film-card")

        for film_card in film_cards:
            title = film_card.find("span", itemprop="name").text
            url = film_card.a.get("href")

            film_html = get_cached_soup(BASE_URL + url, "nziff")

            try:
                minutes = film_html.find("span", itemprop="duration").text.split(" ")[0]
            except AttributeError:
                minutes = 0

            duration_delta = timedelta(minutes=int(minutes))

            film = Film(title, duration_delta)

            session = Session(film, Venue("Venue"), arrow.utcnow(), "http://google.com")

            sessions.append(session)

        self.sessions = sessions