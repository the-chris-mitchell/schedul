import arrow
from sqlmodel import Session
from textual.app import App, ComposeResult
from textual.containers import VerticalScroll
from textual.screen import Screen
from textual.widgets import Checkbox, Collapsible, Footer, Select

from schedul.clients.sql import engine
from schedul.models.bookings import BookingCreate, BookingScreening
from schedul.models.enums import DayBucket, TimeBucket
from schedul.models.preference import ScheduleRequest, TimePreference, VenuePreference
from schedul.models.screening import ScoredScreening
from schedul.models.watchlist import WatchlistEntryCreate, WatchlistFilm
from schedul.services.bookings import (
    create_booking_if_required_db,
    delete_booking_db,
    get_booking_screenings,
)
from schedul.services.schedule import get_festival_schedule
from schedul.services.watchlist import (
    create_watchlist_entry_if_required_db,
    delete_watchlist_entry_db,
    get_watchlist_db,
)

schedule_request: ScheduleRequest = ScheduleRequest(
    time_zone="Pacific/Auckland",
    user_uuid="bf9247fc-df6c-4054-9f46-32a720c8c667",  # type: ignore
    watchlist_only=True,
    venue_preferences=[
        VenuePreference(venue_name="Embassy Theatre", score=5),
        VenuePreference(venue_name="Light House Cinema Cuba", score=4),
        VenuePreference(venue_name="Roxy Cinema", score=1),
    ],
    time_preferences=[
        TimePreference(
            day_bucket=DayBucket.WEEKDAY, time_bucket=TimeBucket.LATE, score=7
        ),
        TimePreference(
            day_bucket=DayBucket.WEEKDAY, time_bucket=TimeBucket.MORNING, score=10
        ),
        TimePreference(
            day_bucket=DayBucket.WEEKDAY,
            time_bucket=TimeBucket.EARLY_AFTERNOON,
            score=5,
        ),
        TimePreference(
            day_bucket=DayBucket.WEEKDAY, time_bucket=TimeBucket.LATE_AFTERNOON, score=3
        ),
        TimePreference(
            day_bucket=DayBucket.WEEKEND, time_bucket=TimeBucket.LATE, score=10
        ),
        TimePreference(
            day_bucket=DayBucket.WEEKEND, time_bucket=TimeBucket.MORNING, score=4
        ),
        TimePreference(
            day_bucket=DayBucket.WEEKEND,
            time_bucket=TimeBucket.EARLY_AFTERNOON,
            score=3,
        ),
        TimePreference(
            day_bucket=DayBucket.WEEKEND, time_bucket=TimeBucket.LATE_AFTERNOON, score=1
        ),
    ],
    max_daily_screenings=1,
)


class WatchlistScreen(Screen):
    def compose(self) -> ComposeResult:
        with Session(engine) as session:
            watchlist: list[WatchlistFilm] = get_watchlist_db(
                session=session, user_uuid=schedule_request.user_uuid
            )
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
                create_watchlist_entry_if_required_db(
                    session=session,
                    watchlist_entry=WatchlistEntryCreate(user_uuid=schedule_request.user_uuid, film_id=int(event.control.id.strip("id_"))),  # type: ignore
                )
            else:
                delete_watchlist_entry_db(
                    session=session,
                    user_uuid=schedule_request.user_uuid,
                    film_id=int(event.control.id.strip("id_")),  # type: ignore
                )


class ScreeningsScreen(Screen):
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
                        label=entry.screening.format(
                            time_zone=schedule_request.time_zone
                        ),
                        id=f"id_{str(entry.screening.id)}",
                        value=entry.is_booked,
                    )
        yield Footer()

    def on_checkbox_changed(self, event: Checkbox.Changed):
        with Session(engine) as session:
            if event.control.value:
                create_booking_if_required_db(
                    session=session,
                    booking=BookingCreate(
                        user_uuid=schedule_request.user_uuid,
                        screening_id=int(event.control.id.strip("id_")),  # type: ignore
                    ),
                )
            else:
                delete_booking_db(
                    session=session,
                    user_uuid=schedule_request.user_uuid,
                    screening_id=int(event.control.id.strip("id_")),  # type: ignore
                )


class ScheduleScreen(Screen):
    schedule: list[ScoredScreening]

    def get_data(self):
        with Session(engine) as session:
            self.schedule = get_festival_schedule(
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
                        label=entry.format(time_zone=schedule_request.time_zone),
                        id=f"id_{str(entry.screening.id)}",
                        value=entry.booked,
                    )
        yield Footer()

    def on_checkbox_changed(self, event: Checkbox.Changed):
        with Session(engine) as session:
            if event.control.value:
                create_booking_if_required_db(
                    session=session,
                    booking=BookingCreate(
                        user_uuid=schedule_request.user_uuid,
                        screening_id=int(event.control.id.strip("id_")),  # type: ignore
                    ),
                )
            else:
                delete_booking_db(
                    session=session,
                    user_uuid=schedule_request.user_uuid,
                    screening_id=int(event.control.id.strip("id_")),  # type: ignore
                )


class UserScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Select([("User 1", 1), ("User 2", 2)])
        yield Footer()


class CheckboxApp(App):
    SCREENS = {
        "watchlist": WatchlistScreen(),
        "user": UserScreen(),
        "screenings": ScreeningsScreen,
        "schedule": ScheduleScreen,
    }
    BINDINGS = [
        ("u", "push_screen('user')", "Users"),
        ("w", "push_screen('watchlist')", "Watchlist"),
        ("s", "push_screen('screenings')", "Screenings"),
        ("x", "push_screen('schedule')", "Schedule"),
    ]

    def on_mount(self):
        self.push_screen(ScheduleScreen())


if __name__ == "__main__":
    CheckboxApp().run()
