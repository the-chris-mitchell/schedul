import uuid as uuid_pkg
import arrow
from sqlmodel import Session
from textual.app import App, ComposeResult
from textual.containers import VerticalScroll, Horizontal
from textual.screen import Screen
from textual.widgets import Checkbox, Collapsible, Footer, Select, Button, Input, Static

from schedul.clients.sql import engine
from schedul.models.bookings import BookingCreate, BookingScreening
from schedul.models.enums import DayBucket, TimeBucket
from schedul.models.preference import ScheduleRequest, TimePreference, VenuePreference
from schedul.models.screening import ScoredScreening
from schedul.models.user import User
from schedul.models.watchlist import WatchlistEntryCreate, WatchlistFilm
from schedul.services.bookings import (
    create_booking_if_required_db,
    delete_booking_db,
    get_booking_screenings,
)
from schedul.services.schedule import get_festival_schedule
from schedul.services.users import (
    create_user_if_required_db,
    delete_user_db,
    get_users_db,
)
from schedul.services.watchlist import (
    create_watchlist_entry_if_required_db,
    delete_watchlist_entry_db,
    get_watchlist_db,
)

# Global variable to hold the schedule request once a user is selected
schedule_request: ScheduleRequest | None = None


def create_default_schedule_request(user_uuid: uuid_pkg.UUID) -> ScheduleRequest:
    """Create a default schedule request for a given user."""
    return ScheduleRequest(
        time_zone="Pacific/Auckland",
        user_uuid=user_uuid,
        watchlist_only=False,
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
                day_bucket=DayBucket.WEEKDAY,
                time_bucket=TimeBucket.LATE_AFTERNOON,
                score=3,
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
                day_bucket=DayBucket.WEEKEND,
                time_bucket=TimeBucket.LATE_AFTERNOON,
                score=1,
            ),
        ],
        max_daily_screenings=1,
    )


class WatchlistScreen(Screen):
    def compose(self) -> ComposeResult:
        if schedule_request is None:
            yield Static("Please select a user first.", classes="error")
            yield Footer()
            return

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
        if schedule_request is None:
            return

        with Session(engine) as session:
            if event.control.value:
                create_watchlist_entry_if_required_db(
                    session=session,
                    watchlist_entry=WatchlistEntryCreate(
                        user_uuid=schedule_request.user_uuid,
                        film_id=int(event.control.id.strip("id_")),  # type: ignore
                    ),
                )
            else:
                delete_watchlist_entry_db(
                    session=session,
                    user_uuid=schedule_request.user_uuid,
                    film_id=int(event.control.id.strip("id_")),  # type: ignore
                )

        # Refresh the schedule screen to reflect watchlist changes
        self._refresh_schedule_if_exists()

    def _refresh_schedule_if_exists(self) -> None:
        """Refresh the schedule screen if it exists in the screen stack."""
        # Check if there's a schedule screen in the app's screen stack
        for screen in self.app.screen_stack:
            if isinstance(screen, ScheduleScreen):
                # Found a schedule screen, refresh it
                screen.refresh_schedule()
                break


class ScreeningsScreen(Screen):
    def compose(self) -> ComposeResult:
        if schedule_request is None:
            yield Static("Please select a user first.", classes="error")
            yield Footer()
            return

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
        if schedule_request is None:
            return

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

        # Refresh the schedule screen to reflect booking changes
        self._refresh_schedule_if_exists()

    def _refresh_schedule_if_exists(self) -> None:
        """Refresh the schedule screen if it exists in the screen stack."""
        # Check if there's a schedule screen in the app's screen stack
        for screen in self.app.screen_stack:
            if isinstance(screen, ScheduleScreen):
                # Found a schedule screen, refresh it
                screen.refresh_schedule()
                break


class ScheduleScreen(Screen):
    schedule: list[ScoredScreening]

    def get_data(self):
        if schedule_request is None:
            self.schedule = []
            return

        with Session(engine) as session:
            self.schedule = get_festival_schedule(
                session=session, festival_id=1, schedule_request=schedule_request
            )

    def compose(self) -> ComposeResult:
        if schedule_request is None:
            yield Static("Please select a user first.", classes="error")
            yield Footer()
            return

        self.get_data()

        with VerticalScroll(id="schedule_content"):
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
        if schedule_request is None:
            return

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

    def refresh_schedule(self) -> None:
        """Refresh the schedule data and update the display."""
        if schedule_request is None:
            return

        # Get fresh data
        self.get_data()

        # Find the schedule content container and refresh it
        try:
            scroll_container = self.query_one("#schedule_content", VerticalScroll)

            # Clear existing content
            scroll_container.remove_children()

            # Rebuild the content
            days = sorted(
                {
                    arrow.get(entry.screening.start_time_utc)
                    .to(schedule_request.time_zone)
                    .date()
                    for entry in self.schedule
                }
            )

            # Create and mount new content
            for day in days:
                collapsible = Collapsible(
                    title=arrow.get(day).format(fmt="dddd Do MMMM"), collapsed=False
                )
                scroll_container.mount(collapsible)

                # Create checkboxes for this day
                day_entries = [
                    entry
                    for entry in self.schedule
                    if arrow.get(entry.screening.start_time_utc)
                    .to(schedule_request.time_zone)
                    .date()
                    == day
                ]

                for entry in day_entries:
                    checkbox = Checkbox(
                        label=entry.format(time_zone=schedule_request.time_zone),
                        id=f"id_{str(entry.screening.id)}",
                        value=entry.booked,
                    )
                    collapsible.mount(checkbox)

        except Exception:
            # If we can't find the container or there's an error, fall back to creating a new screen
            # This might happen if the screen isn't fully composed yet
            self.app.push_screen(ScheduleScreen())


class UserScreen(Screen):
    CSS = """
    .hidden {
        display: none;
    }
    """

    def compose(self) -> ComposeResult:
        with Session(engine) as session:
            users = get_users_db(session)

        yield Static("User Management", classes="title")

        # User selection
        if users:
            user_options: list[tuple[str, uuid_pkg.UUID]] = [
                (f"{user.name}", user.uuid) for user in users
            ]
            user_select = Select(
                options=user_options, prompt="Select a user", id="user_select"
            )
            # Set the value only if we have a valid schedule_request and the user exists in options
            if schedule_request and any(
                uuid == schedule_request.user_uuid for _, uuid in user_options
            ):
                user_select.value = schedule_request.user_uuid
            yield user_select
        else:
            yield Static("No users found. Click 'Create User' to add a new user.")

        # Create User button (always visible)
        yield Button("Create User", id="create_user_btn")

        # User creation form (initially hidden)
        with Static(id="user_creation_form", classes="hidden"):
            yield Static("Create New User:")
            yield Input(
                placeholder="Enter user name", id="new_user_name", classes="user_input"
            )
            with Horizontal():
                yield Button("Save User", id="save_user_btn")
                yield Button("Cancel", id="cancel_user_btn", variant="error")

        # User deletion (only show if users exist)
        if users:
            yield Button("Delete Selected User", id="delete_user_btn", variant="error")

        yield Static("", id="status_message")
        yield Footer()

    def on_select_changed(self, event: Select.Changed) -> None:
        """Handle user selection change."""
        if (
            event.control.id == "user_select"
            and event.value
            and isinstance(event.value, uuid_pkg.UUID)
        ):
            global schedule_request
            # Create schedule request for the selected user
            schedule_request = create_default_schedule_request(event.value)

            # Get user name for display
            with Session(engine) as session:
                users = get_users_db(session)
                selected_user = next(
                    (user for user in users if user.uuid == event.value), None
                )
                user_display = selected_user.name if selected_user else str(event.value)

            self.query_one("#status_message", Static).update(
                f"Selected user: {user_display}"
            )

            # Automatically navigate to screenings screen
            self.app.push_screen("screenings")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "create_user_btn":
            self._show_create_form()
        elif event.button.id == "save_user_btn":
            self._create_user()
        elif event.button.id == "cancel_user_btn":
            self._hide_create_form()
        elif event.button.id == "delete_user_btn":
            self._delete_user()

    def _show_create_form(self) -> None:
        """Show the user creation form."""
        form = self.query_one("#user_creation_form", Static)
        form.remove_class("hidden")
        # Focus on the name input
        name_input = self.query_one("#new_user_name", Input)
        name_input.focus()

    def _hide_create_form(self) -> None:
        """Hide the user creation form."""
        form = self.query_one("#user_creation_form", Static)
        form.add_class("hidden")
        # Clear the input
        name_input = self.query_one("#new_user_name", Input)
        name_input.value = ""
        # Clear any status message
        self.query_one("#status_message", Static).update("")

    def _create_user(self) -> None:
        """Create a new user."""
        name_input = self.query_one("#new_user_name", Input)

        # Validate name
        if not name_input.value.strip():
            self.query_one("#status_message", Static).update("User name is required.")
            return

        user_name = name_input.value.strip()

        # Always generate a new UUID
        user_uuid = uuid_pkg.uuid4()

        # Create user in database
        with Session(engine) as session:
            user = User(uuid=user_uuid, name=user_name)
            try:
                created_user = create_user_if_required_db(session, user)
            except Exception as e:
                self.query_one("#status_message", Static).update(
                    f"Error creating user: {str(e)}"
                )
                return

        # Update global schedule request
        global schedule_request
        schedule_request = create_default_schedule_request(created_user.uuid)

        # Hide the form
        self._hide_create_form()

        # Show status and navigate to screenings
        self.query_one("#status_message", Static).update(
            f"Created and selected user: {created_user.name}"
        )

        # Navigate to screenings screen after creating user
        self.app.push_screen("screenings")

    def _delete_user(self) -> None:
        """Delete the selected user."""
        user_select = self.query_one("#user_select", Select)

        if not user_select.value or not isinstance(user_select.value, uuid_pkg.UUID):
            self.query_one("#status_message", Static).update(
                "No user selected for deletion."
            )
            return

        selected_uuid = user_select.value

        # Get user name before deletion for display
        with Session(engine) as session:
            users = get_users_db(session)
            selected_user = next(
                (user for user in users if user.uuid == selected_uuid), None
            )
            user_name = selected_user.name if selected_user else "Unknown"

        with Session(engine) as session:
            success = delete_user_db(session, selected_uuid)

        if success:
            self.query_one("#status_message", Static).update(
                f"Deleted user: {user_name}"
            )

            # If we deleted the currently selected user, clear the schedule request
            global schedule_request
            if schedule_request and schedule_request.user_uuid == selected_uuid:
                schedule_request = None
                self.query_one("#status_message", Static).update(
                    f"Deleted user: {user_name}. Please select another user."
                )

            # Refresh the screen to update the user list
            self.app.push_screen(UserScreen())
        else:
            self.query_one("#status_message", Static).update("Failed to delete user.")


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
        # Check if there's only one user in the database
        with Session(engine) as session:
            users = get_users_db(session)

        if len(users) == 1:
            # Auto-select the single user and go to screenings screen
            global schedule_request
            schedule_request = create_default_schedule_request(users[0].uuid)
            self.push_screen("schedule")
        else:
            # Show user selection screen
            self.push_screen(UserScreen())

    async def action_push_screen(self, screen: str) -> None:
        """Override push_screen action to prevent access to screens without user selection."""
        # Allow access to user screen always
        if screen == "user":
            await super().action_push_screen(screen)
            return

        # Check if user is selected for other screens
        if schedule_request is None:
            # Push user screen instead and show a message
            await self.push_screen(UserScreen())
            # You could add a notification here if the framework supports it
            return

        # User is selected, allow access to the requested screen
        await super().action_push_screen(screen)


if __name__ == "__main__":
    CheckboxApp().run()
