from datetime import date, datetime, time, timedelta
from enum import Enum


class Film:
    def __init__(self, name: str, runtime: timedelta):
        self.name = name
        self.runtime = runtime

class Venue:
    def __init__(self, name: str):
        self.name = name

class Session:
    def __init__(self, film: Film, venue: Venue, start_time: datetime, link: str):
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

    def book(self):
        self.booked = True

    def format(self):
        return f"{'✅' if self.booked else '👀'} {self.start_time_formatted}-{self.end_time_formatted}: {self.film.name} ({int(self.film.runtime.seconds/60)} minutes) @ {self.venue.name}"


    def get_end_time(self):
        return self.start_time + self.film.runtime

    def get_day_bucket(self):
        match datetime.fromisoformat(str(self.start_time)).date().weekday():
            case 5 | 6:
                return DayBucket.WEEKEND
            case 4:
                return DayBucket.FRIDAY
            case 1 | 2 | 3:
                return DayBucket.WEEKDAY
            case _:
                return DayBucket.NONE

    def get_time_bucket(self):
        start_time = datetime.fromisoformat(str(self.start_time)).time()
        if start_time < time(13):
            return TimeBucket.MORNING
        elif start_time < time(17):
            return TimeBucket.AFTERNOON
        elif start_time > time(17):
            return TimeBucket.EVENING
        else:
            return TimeBucket.NONE

class Schedule:
    def __init__(self):
        self.sessions: list[Session] = []
    
    def calculate_score(self, preferences):
        score = 0
        preference: Preference
        for position, preference in enumerate(preferences, start=1):
            position_score = 0
            if preference.date:
                position_score+= len([session for session in self.sessions if session.start_time.date() == preference.date])
            if preference.day_bucket:
                position_score+= len([session for session in self.sessions if session.day_bucket == preference.day_bucket])
            if preference.time_bucket:
                position_score+= len([session for session in self.sessions if session.time_bucket == preference.time_bucket])
            if preference.venue:
                position_score+= len([session for session in self.sessions if session.venue.name == preference.venue.name])

            score += position_score / position

        return score
        

class TimeBucket(Enum):
    NONE = 0
    MORNING = 1
    AFTERNOON = 2
    EVENING = 3

class DayBucket(Enum):
    NONE = 0
    WEEKEND = 1
    WEEKDAY = 2
    FRIDAY = 3

class Preference:
    def __init__(self, time_bucket: TimeBucket=None, day_bucket: DayBucket=None, date: date=None, venue: Venue = None):
        self.day_bucket = day_bucket
        self.time_bucket = time_bucket
        self.date = date
        self.venue = venue
