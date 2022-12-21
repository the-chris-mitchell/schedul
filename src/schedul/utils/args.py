import argparse

from scraper.festivals import FESTIVALS
from scraper.festivals.base import Festival


def get_args(festivals: list[Festival]) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "festival",
        choices=[festival.short_name for festival in festivals],
        help="Select a festival",
    )
    return parser.parse_args()


ARGS = get_args(FESTIVALS)
