import argparse

from festivals import FESTIVALS
from models.festival import Festival

def get_args(festivals: list[Festival]) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("festival", choices=[festival.short_name for festival in festivals], help="Select a festival")
    parser.add_argument("mode", choices=['sessions', 'schedule', 'films', 'films-csv', 'cal'], help="What mode to run")
    return parser.parse_args()

ARGS = get_args(FESTIVALS)