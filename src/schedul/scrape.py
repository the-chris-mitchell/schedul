import click

from schedul.clients.sql import create_db_and_tables
from schedul.scraper.festivals import FESTIVALS
from schedul.scraper.festivals.base import Festival


@click.command()
@click.argument(
    "env",
    type=click.Choice(["dev", "prod"]),
)
@click.argument(
    "festival",
    type=click.Choice([festival.short_name for festival in FESTIVALS]),
)
def main(env: str, festival: str):
    selected_festival: Festival = [
        fest for fest in FESTIVALS if fest.short_name == festival
    ][0]

    if env == "dev":
        create_db_and_tables()
        print(f"Scraping: {selected_festival.full_name}")
        selected_festival.create_resources_dev()
    if env == "prod":
        selected_festival.create_resources_prod()


if __name__ == "__main__":
    main()
