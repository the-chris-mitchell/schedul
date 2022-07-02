from festivals.fff import FrenchFilmFestival
from festivals.flicks import Flicks
from festivals.nziff import NZInternationalFilmFestival
from models.festival import Festival


def get_festivals() -> list[Festival]:
    return [
        FrenchFilmFestival(),
        NZInternationalFilmFestival(),
        Flicks()
    ]