from datetime import date, datetime, time, timedelta

from enums import DayBucket, TimeBucket


class Film:
    def __init__(self, name: str, runtime: timedelta) -> None:
        self.name = name
        self.runtime = runtime

class Venue:
    def __init__(self, name: str) -> None:
        self.name = name

class Session:
    def __init__(self, film: Film, venue: Venue, start_time: datetime, link: str) -> None:
        self.film = film
        self.venue = venue
        self.link = link
        self.start_time = start_time
        self.booked = False
        self.end_time = self.get_end_time()
        self.day_bucket = self.get_day_bucket()
        self.time_bucket = self.get_time_bucket()
        self.start_time_formatted = datetime.fromisoformat(str(start_time)).strftime(f"%a {self.time_bucket.name.capitalize()} (%d/%m) %I:%M%p")
        self.end_time_formatted = datetime.fromisoformat(str(self.end_time)).strftime("%I:%M%p")

    def book(self) -> None:
        self.booked = True

    def format(self) -> str:
        return f"{'✅' if self.booked else '👀'} {self.start_time_formatted}-{self.end_time_formatted}: {self.film.name} ({int(self.film.runtime.seconds/60)} minutes) @ {self.venue.name}"

    def get_end_time(self) -> datetime:
        return self.start_time + self.film.runtime

    def get_day_bucket(self) -> DayBucket:
        match datetime.fromisoformat(str(self.start_time)).date().weekday():
            case 5 | 6:
                return DayBucket.WEEKEND
            case 4:
                return DayBucket.FRIDAY
            case 1 | 2 | 3:
                return DayBucket.WEEKDAY
            case _:
                return DayBucket.NONE

    def get_time_bucket(self) -> TimeBucket:
        start_time = datetime.fromisoformat(str(self.start_time)).time()
        if start_time < time(13):
            return TimeBucket.MORNING
        elif start_time < time(17):
            return TimeBucket.AFTERNOON
        elif start_time > time(17):
            return TimeBucket.EVENING
        else:
            return TimeBucket.NONE

class Preference:
    def __init__(self, time_bucket: TimeBucket=None, day_bucket: DayBucket=None, date: date=None, venue: Venue = None) -> None:
        self.day_bucket = day_bucket
        self.time_bucket = time_bucket
        self.date = date
        self.venue = venue

class Schedule:
    def __init__(self, festival: str) -> None:
        self.sessions: list[Session] = []
        self.festival: str = festival
    
    def calculate_score(self, preferences: list[Preference]) -> float:
        score: float = 0
        for position, preference in enumerate(preferences, start=1):
            position_score = 0
            if preference.date:
                position_score += len([session for session in self.sessions if session.start_time.date() == preference.date])
            if preference.day_bucket:
                position_score += len([session for session in self.sessions if session.day_bucket == preference.day_bucket])
            if preference.time_bucket:
                position_score += len([session for session in self.sessions if session.time_bucket == preference.time_bucket])
            if preference.venue:
                position_score += len([session for session in self.sessions if session.venue.name == preference.venue.name])

            score += position_score / position

        return score

    def sort(self) -> None:
        self.sessions = sorted(self.sessions, key=lambda x: x.start_time)

class Options:
    def __init__(self, iterations: int, max_sessions: int, preferences: list[Preference], excluded_dates: list[date]) -> None:
        self.iterations: int = iterations
        self.max_sessions: int = max_sessions
        self.preferences: list[Preference] = preferences
        self.excluded_dates: list[date] = excluded_dates
