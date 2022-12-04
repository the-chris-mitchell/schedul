
from ics import Calendar, Event # type: ignore
import arrow

from models.preference import Preference
from models.session import Session


class Schedule:
    def __init__(self, festival: str) -> None:
        self.sessions: list[Session] = []
        self.festival = festival
    
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

    def print(self) -> None:
        print("=" * 50)
        print(f"🎬 Schedule for {self.festival} with {len(self.sessions)} films:")
        print("=" * 50)
        for position, week in enumerate(sorted(list(set([session.start_time.isocalendar()[1] for session in self.sessions]))), start=1):
            print(f"\n📆 Week {position}:")
            print("─" * 10)
            for session in [session for session in self.sessions if session.start_time.isocalendar()[1] == week]:
                print(session.format())
                if not session.booked:
                    print(f"↪️ 🔗 {session.link}")
    
    def calendar(self) -> None:
        calendar = Calendar()
        for session in self.sessions:
            event = Event()
            event.name = session.film.name
            event.begin = arrow.get(session.start_time).to('utc')
            event.end = arrow.get(session.end_time).to('utc')
            event.location = session.venue.name
            calendar.events.add(event)
        with open('movies.ics', 'w') as file:
            file.writelines(calendar)