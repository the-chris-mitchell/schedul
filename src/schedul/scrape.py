from scraper.festivals import FESTIVALS
from scraper.festivals.base import Festival
from utils.args import ARGS

selected_festival: Festival = [
    festival for festival in FESTIVALS if festival.short_name == ARGS.festival
][0]

if __name__ == "__main__":
    selected_festival.create_resources()
