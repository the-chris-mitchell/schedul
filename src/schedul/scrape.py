import argparse

from scraper.festivals import FESTIVALS
from scraper.festivals.base import Festival

parser = argparse.ArgumentParser()
parser.add_argument(
    "env",
    choices=["dev", "prod"],
    help="Select an environment",
)
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
    if ARGS.env == "dev":
        selected_festival.create_resources_dev()
    if ARGS.env == "prod":
        selected_festival.create_resources_prod()
