from datetime import date
from models.preference import Preference


class Options:
    def __init__(self, iterations: int, max_sessions: int, preferences: list[Preference], excluded_dates: list[date], booked_links: list[str]) -> None:
        self.iterations = iterations
        self.max_sessions = max_sessions
        self.preferences = preferences
        self.excluded_dates = excluded_dates
        self.booked_links = booked_links