import argparse

from scraper.festivals import FESTIVALS
from scraper.festivals.base import Festival

parser = argparse.ArgumentParser()
parser.add_argument(
    "festival",
    choices=[festival.short_name for festival in FESTIVALS],
    help="Select a festival",
)
ARGS = parser.parse_args()


selected_festival: Festival = [
    festival for festival in FESTIVALS if festival.short_name == ARGS.festival
][0]

if __name__ == "__main__":
    selected_festival.create_resources()
