import re
from datetime import timedelta

import requests_cache
from bs4 import BeautifulSoup
from dateutil import parser

from models import Film, Session, Venue

URL = "https://www.frenchfilmfestival.co.nz/locations/Wellington"

WATCHLIST = [
    #"Another World",
    "Between Two Worlds",
    "Everything Went Fine",
    "Farewell, Mr. Haffmann",
    "La Traviata, My Brothers and I",
    "Love Songs for Tough Guys",
    "Madeleine Collins"
]

MY_VENUES = [
    "Light House Cuba",
    "Embassy Theatre",
    "Light House Pauatahanui",
    "Light House Petone",
    "Penthouse Cinema & Cafe"
]

requests_session = requests_cache.CachedSession('fff')

response = requests_session.get(URL)

soup = BeautifulSoup(response.text, features="html.parser")

venues_html = soup.find_all("div", attrs={"class": "venue-film-list"})

def get_sessions():
    sessions = []

    for venue_html in venues_html:
        for movie in venue_html.find_all("div", attrs={"class": "venue-film"}):
            film = Film(
                movie.find("h3").find("a").text,
                timedelta(minutes=int(movie.find("span", attrs={"class": "film-runtime"}).text.split(" ")[0]))
            )
            
            venue_name = venue_html.find("h2").text

            if film.name not in WATCHLIST:
                continue
            if venue_name not in MY_VENUES:
                continue

            embassy_screen_data = {
                "https://www.eventcinemas.co.nz/Orders/Tickets#sessionId=1633315&bookingSource=www|movies": "Deluxe",
                "https://www.eventcinemas.co.nz/Orders/Tickets#sessionId=1633576&bookingSource=www|movies": "Deluxe",
                "https://www.eventcinemas.co.nz/Orders/Tickets#sessionId=1633282&bookingSource=www|movies": "Deluxe",
                "https://www.eventcinemas.co.nz/Orders/Tickets#sessionId=1633574&bookingSource=www|movies": "Deluxe",
                "https://www.eventcinemas.co.nz/Orders/Tickets#sessionId=1633287&bookingSource=www|movies": "Deluxe",
                "https://www.eventcinemas.co.nz/Orders/Tickets#sessionId=1633288&bookingSource=www|movies": "Deluxe",
                "https://www.eventcinemas.co.nz/Orders/Tickets#sessionId=1633599&bookingSource=www|movies": "The Grand",
                "https://www.eventcinemas.co.nz/Orders/Tickets#sessionId=1633280&bookingSource=www|movies": "Deluxe",
                "https://www.eventcinemas.co.nz/Orders/Tickets#sessionId=1633596&bookingSource=www|movies": "The Grand",
                "https://www.eventcinemas.co.nz/Orders/Tickets#sessionId=1633278&bookingSource=www|movies": "Deluxe",
                "https://www.eventcinemas.co.nz/Orders/Tickets#sessionId=1633277&bookingSource=www|movies": "Deluxe",
                "https://www.eventcinemas.co.nz/Orders/Tickets#sessionId=1633314&bookingSource=www|movies": "Deluxe",
                "https://www.eventcinemas.co.nz/Orders/Tickets#sessionId=1633604&bookingSource=www|movies": "The Grand",
                "https://www.eventcinemas.co.nz/Orders/Tickets#sessionId=1633318&bookingSource=www|movies": "Deluxe",
                "https://www.eventcinemas.co.nz/Orders/Tickets#sessionId=1633302&bookingSource=www|movies": "Deluxe",
                "https://www.eventcinemas.co.nz/Orders/Tickets#sessionId=1633308&bookingSource=www|movies": "Deluxe",
                "https://www.eventcinemas.co.nz/Orders/Tickets#sessionId=1633312&bookingSource=www|movies": "Deluxe",
                "https://www.eventcinemas.co.nz/Orders/Tickets#sessionId=1633590&bookingSource=www|movies": "Deluxe",
                "https://www.eventcinemas.co.nz/Orders/Tickets#sessionId=1633310&bookingSource=www|movies": "Deluxe",
                "https://www.eventcinemas.co.nz/Orders/Tickets#sessionId=1633306&bookingSource=www|movies": "Deluxe",
            }

            for session_html in movie.find_all("p", attrs={"class": "sessionLine"}):
                link = session_html.a['href']
                if venue_name == "Embassy Theatre":
                    venue = Venue(f"Embassy Theatre {embassy_screen_data[link]}")
                else:
                    venue = Venue(venue_name)

                session_date = re.search("(.+)\|(.+m)", session_html.text).group(1).strip()
                session_time = re.search("(.+)\|(.+m)", session_html.text).group(2).strip().replace(".", ":")
                session = Session(
                    film,
                    venue,
                    parser.parse(f"{session_date} {session_time}"),
                    link
                )

                sessions.append(session)

    return sessions
