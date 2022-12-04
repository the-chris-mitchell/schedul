from datetime import timedelta
from dateutil import parser # type: ignore

from clients import get_cached_soup, get_selenium_soup

from models import Film, Session, Venue


BASE_URL = "https://www.flicks.co.nz"
VENUES_URL = BASE_URL + "/cinemas/wellington/"


soup = get_cached_soup(VENUES_URL, "flicks", timedelta(days=1))

venues_html = soup.find_all("a", attrs={"class": "cinema-list__title"})

def get_sessions() -> list[Session]:
    sessions: list[Session] = []

    for venue_html in venues_html[2:]:
        venue = Venue(venue_html.text)
        movies_soup = get_selenium_soup(BASE_URL + venue_html['href'])

        for day_soup in movies_soup.find_all("div", attrs={"class": "timetable__day"}):
            session_date = day_soup["data-date"]

            for movie in day_soup.find_all("article", attrs={"class": "timetable__article"}):
                runtime = get_flicks_runtime(movie)

                film = Film(
                    movie.find("h3").text,
                    timedelta(minutes=runtime)
                )
            
                for session_html in movie.find_all("li", attrs={"class": "times-calendar-times__el"}):
                    link = session_html.a['href']

                    session_time = session_html.span.text

                    session = Session(
                        film,
                        venue,
                        parser.parse(f"{session_date} {session_time}"),
                        link
                    )

                    print(session.format())

                    sessions.append(session)

    return sessions

def get_flicks_runtime(movie):
    icons = movie.find_all("span", attrs={"class": "cinema__movie-icon"})
    runtime = 0
    for icon in icons:
        if "m" in icon.text:
            runtime = int(icon.text.replace("m", ""))
    return runtime

get_sessions()
