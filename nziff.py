from datetime import timedelta
from bs4 import BeautifulSoup # type: ignore
import requests_cache

from models import Film

BASE_URL = "https://www.nziff.co.nz"
URL = BASE_URL + "/nziff-2022/2022/films/title/"

def get_soup(url: str, cache: str):
    requests_session = requests_cache.CachedSession(cache)

    response = requests_session.get(url)

    return BeautifulSoup(response.text, features="html.parser")
    return soup

soup = get_soup(URL, "nziff")

film_cards =  soup.find_all("article", class_="film-card")

films: list[Film] = []

for film_card in film_cards:
    title = film_card.find("span", itemprop="name").text
    url = film_card.a.get("href")

    film_html = get_soup(BASE_URL + url, "nziff")

    minutes = film_html.find("span", itemprop="duration").text.split(" ")[0]

    duration_delta = timedelta(minutes=int(minutes))

    films.append(Film(title, duration_delta))

for film in films:
    print(f"{film.name}, {film.runtime}")