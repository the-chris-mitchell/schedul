import arrow
from sqlmodel import Session
from textual.app import App, ComposeResult
from textual.containers import VerticalScroll
from textual.screen import Screen
from textual.widgets import Checkbox, Collapsible, Footer, Select

from clients.sql import engine
from models.bookings import BookingScreening
from models.enums import DayBucket, TimeBucket
from models.preference import ScheduleRequest, TimePreference
from models.screening import ScoredScreening
from models.watchlist import WatchlistFilm
from services.bookings import (
    create_booking_db,
    delete_booking_db,
    get_booking_screenings,
)
from services.festival import get_festival_schedule_db
from services.watchlist import (
    create_watchlist_entry_db,
    delete_watchlist_entry_db,
    get_watchlist_db,
)

schedule_request: ScheduleRequest = ScheduleRequest(
    time_zone="Pacific/Auckland",
    user_uuid="bf9247fc-df6c-4054-9f46-32a720c8c667",
    venues=["Embassy Theatre", "Light House Cinema Cuba", "Roxy Cinema"],
    watchlist_only=False,
    time_preferences=[
        TimePreference(day_bucket=DayBucket.WEEKDAY, time_bucket=TimeBucket.LATE),
        TimePreference(day_bucket=DayBucket.WEEKDAY, time_bucket=TimeBucket.MORNING),
        TimePreference(
            day_bucket=DayBucket.WEEKDAY, time_bucket=TimeBucket.EARLY_AFTERNOON
        ),
        TimePreference(
            day_bucket=DayBucket.WEEKDAY, time_bucket=TimeBucket.LATE_AFTERNOON
        ),
        TimePreference(day_bucket=DayBucket.WEEKEND, time_bucket=TimeBucket.LATE),
        TimePreference(day_bucket=DayBucket.WEEKEND, time_bucket=TimeBucket.MORNING),
        TimePreference(
            day_bucket=DayBucket.WEEKEND, time_bucket=TimeBucket.EARLY_AFTERNOON
        ),
        TimePreference(
            day_bucket=DayBucket.WEEKEND, time_bucket=TimeBucket.LATE_AFTERNOON
        ),
    ],
    max_daily_sessions=2,
)


class WatchlistScreen(Screen):
    def compose(self) -> ComposeResult:
        with Session(engine) as session:
            watchlist: list[WatchlistFilm] = get_watchlist_db(
                session=session, user_uuid=schedule_request.user_uuid
            ).films
        with VerticalScroll():
            for entry in watchlist:
                yield Checkbox(
                    label=entry.film.name,
                    id=f"id_{str(entry.film.id)}",
                    value=entry.in_watchlist,
                )
        yield Footer()

    def on_checkbox_changed(self, event: Checkbox.Changed):
        with Session(engine) as session:
            if event.control.value:
                create_watchlist_entry_db(
                    session=session,
                    user_uuid=schedule_request.user_uuid,
                    film_id=int(event.control.id.strip("id_")),
                )
            else:
                delete_watchlist_entry_db(
                    session=session,
                    user_uuid=schedule_request.user_uuid,
                    film_id=int(event.control.id.strip("id_")),
                )


class SessionsScreen(Screen):
    def compose(self) -> ComposeResult:
        with Session(engine) as session:
            bookings: list[BookingScreening] = get_booking_screenings(
                session=session, user_uuid=schedule_request.user_uuid
            )
        days = sorted(
            {
                arrow.get(entry.screening.start_time_utc)
                .to(schedule_request.time_zone)
                .date()
                for entry in bookings
            }
        )
        for day in days:
            with Collapsible(
                title=arrow.get(day).format(fmt="dddd Do MMMM"), collapsed=False
            ):
                for entry in sorted(
                    [
                        entry
                        for entry in bookings
                        if arrow.get(entry.screening.start_time_utc)
                        .to(schedule_request.time_zone)
                        .date()
                        == day
                    ],
                    key=lambda item: item.screening.start_time_utc,
                ):
                    yield Checkbox(
                        label=f"{entry.film.name} @ {entry.venue.name} @ {arrow.get(entry.screening.start_time_utc).to(schedule_request.time_zone).format(arrow.FORMAT_RFC2822)}",
                        id=f"id_{str(entry.screening.id)}",
                        value=entry.is_booked,
                    )
        yield Footer()

    def on_checkbox_changed(self, event: Checkbox.Changed):
        with Session(engine) as session:
            if event.control.value:
                create_booking_db(
                    session=session,
                    user_uuid=schedule_request.user_uuid,
                    screening_id=int(event.control.id.strip("id_")),
                )
            else:
                delete_booking_db(
                    session=session,
                    user_uuid=schedule_request.user_uuid,
                    screening_id=int(event.control.id.strip("id_")),
                )


class ScheduleScreen(Screen):
    schedule: list[ScoredScreening]

    def get_data(self):
        with Session(engine) as session:
            self.schedule = get_festival_schedule_db(
                session=session, festival_id=1, schedule_request=schedule_request
            )

    def compose(self) -> ComposeResult:
        self.get_data()
        days = sorted(
            {
                arrow.get(entry.screening.start_time_utc)
                .to(schedule_request.time_zone)
                .date()
                for entry in self.schedule
            }
        )
        for day in days:
            with Collapsible(
                title=arrow.get(day).format(fmt="dddd Do MMMM"), collapsed=False
            ):
                for entry in [
                    entry
                    for entry in self.schedule
                    if arrow.get(entry.screening.start_time_utc)
                    .to(schedule_request.time_zone)
                    .date()
                    == day
                ]:
                    yield Checkbox(
                        label=f"{'👀' if entry.in_watchlist else ''} {entry.screening.film.name} @ {entry.screening.venue.name} @ {arrow.get(entry.screening.start_time_utc).to(schedule_request.time_zone).format(arrow.FORMAT_RFC2822)} ({entry.time_bucket.name})",
                        id=f"id_{str(entry.screening.id)}",
                        value=entry.booked,
                    )
        yield Footer()

    def on_checkbox_changed(self, event: Checkbox.Changed):
        with Session(engine) as session:
            if event.control.value:
                create_booking_db(
                    session=session,
                    user_uuid=schedule_request.user_uuid,
                    screening_id=int(event.control.id.strip("id_")),
                )
            else:
                delete_booking_db(
                    session=session,
                    user_uuid=schedule_request.user_uuid,
                    screening_id=int(event.control.id.strip("id_")),
                )


class UserScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Select([("User 1", 1), ("User 2", 2)])
        yield Footer()


class CheckboxApp(App):
    SCREENS = {
        "watchlist": WatchlistScreen(),
        "user": UserScreen(),
        "sessions": SessionsScreen,
        "schedule": ScheduleScreen,
    }
    BINDINGS = [
        ("u", "push_screen('user')", "Users"),
        ("w", "push_screen('watchlist')", "Watchlist"),
        ("s", "push_screen('sessions')", "Sessions"),
        ("x", "push_screen('schedule')", "Schedule"),
    ]

    def on_mount(self):
        self.push_screen(ScheduleScreen())


if __name__ == "__main__":
    CheckboxApp().run()