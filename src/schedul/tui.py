from sqlmodel import Session
from textual.app import App, ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import RadioButton

from clients.sql import engine
from models.watchlist import WatchlistFilm
from services.watchlist import (
    create_watchlist_entry_db,
    delete_watchlist_entry_db,
    get_watchlist_db,
)

with Session(engine) as session:
    WATCHLIST: list[WatchlistFilm] = get_watchlist_db(
        session=session, user_uuid="bf9247fc-df6c-4054-9f46-32a720c8c667"
    ).films


class CheckboxApp(App[None]):
    def compose(self) -> ComposeResult:
        with VerticalScroll():
            for entry in WATCHLIST:
                yield RadioButton(
                    label=entry.film.name,
                    id=f"id_{str(entry.film.id)}",
                    value=entry.in_watchlist,
                )

    def on_radio_button_changed(self, event: RadioButton.Changed):
        with Session(engine) as session:
            if event.control.value:
                create_watchlist_entry_db(
                    session=session,
                    user_uuid="bf9247fc-df6c-4054-9f46-32a720c8c667",
                    film_id=int(event.control.id.strip("id_")),
                )
            else:
                delete_watchlist_entry_db(
                    session=session,
                    user_uuid="bf9247fc-df6c-4054-9f46-32a720c8c667",
                    film_id=int(event.control.id.strip("id_")),
                )


if __name__ == "__main__":
    CheckboxApp().run()
