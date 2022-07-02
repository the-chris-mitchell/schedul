import csv
import re
from datetime import timedelta
from math import ceil

from tqdm import tqdm # type: ignore

from .soup import get_cached_soup, get_rendered_soup

USER = "chrismitchell"
URL = f"https://letterboxd.com/{USER}/watchlist"



def set_watchlist() -> None:
    soup = get_cached_soup(URL, "letterboxd", timedelta(days=1))

    watchlist_count = soup.find("div", attrs={"class": "js-watchlist-content"})["data-num-entries"]

    pages = ceil(int(watchlist_count) / 28)

    movies = []

    for page in tqdm(range(1, int(pages) + 1)):
        rendered_soup = get_rendered_soup(f"{URL}/page/{page}/")
        movies_html = rendered_soup.find_all("span", attrs={"class": "frame-title"})

        for movie_html in movies_html:
            try:
                title = re.search("(.+) \((.+)\)", movie_html.text)[1] # type: ignore
                year = re.search("(.+) \((.+)\)", movie_html.text)[2] # type: ignore
            except TypeError:
                title = movie_html.text
                year = "unknown"
            movies.append({"title": title, "year": year})


    with open('watchlist.csv', 'w', newline='') as file:
        dict_writer = csv.DictWriter(file, movies[0].keys())
        dict_writer.writeheader()
        dict_writer.writerows(movies)


def get_watchlist() -> list[str]:
    with open('watchlist.csv', 'r') as file:
        dict_reader = csv.DictReader(file)
        return [film["title"] for film in dict_reader]
