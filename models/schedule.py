from datetime import timedelta
import random
from ics import Calendar, Event # type: ignore
from tqdm import tqdm # type: ignore
import arrow # type: ignore
from models.options import Options

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

    def get_formatted(self) -> str:
        lines: list[str] = []
        lines.append("=" * 50)
        lines.append(f"🎬 Schedule for {self.festival} with {len(self.sessions)} films:")
        lines.append("=" * 50)
        for position, week in enumerate(sorted(list({session.start_time.isocalendar()[1] for session in self.sessions})), start=1):
            lines.append(f"\n📆 Week {position}:")
            lines.append("─" * 10)
            for session in [session for session in self.sessions if session.start_time.isocalendar()[1] == week]:
                lines.append(session.format())
                if not session.booked:
                    lines.append(f"↪️ 🔗 {session.link}")
        return "\n".join(lines)
    
    def save_calendar(self, filename: str) -> None:
        calendar = Calendar()
        for session in self.sessions:
            event = Event()
            event.name = session.film.name
            event.begin = arrow.get(session.start_time).to('utc')
            event.end = arrow.get(session.end_time).to('utc')
            event.location = session.venue.name
            calendar.events.add(event)
        with open(filename, 'w') as file:
            file.writelines(calendar)
        print(f"Saved calendar to {filename}")

    def try_add_session(self, session: Session, options: Options) -> None:
        if session.start_time.date() in options.excluded_dates:
            return
        if any(entry.film.name == session.film.name for entry in self.sessions):
            return
        if any(entry.start_time <= (session.end_time + timedelta(minutes=30)) and session.start_time <= (entry.end_time + timedelta(minutes=30)) for entry in self.sessions):
            return
        if len([x for x in self.sessions if x.start_time.date() == session.start_time.date()]) == options.max_sessions:
            return
        self.sessions.append(session)


def get_schedule(options: Options, sessions: list[Session], festival: str) -> Schedule:

    all_schedules: list[Schedule] = []

    for _ in tqdm(range(options.iterations)):
        current_schedule = Schedule(festival)

        booked_sessions = [session for session in sessions if session.link in options.booked_links]

        for session in booked_sessions:
            session.book()

        current_schedule.sessions.extend(booked_sessions)

        shuffled_sessions: list[Session] = random.sample(sessions, k=len(sessions))

        for preference in options.preferences:
            for session in shuffled_sessions:
                if preference.date and session.start_time.date() != preference.date:
                    continue
                if preference.day_bucket and session.day_bucket != preference.day_bucket:
                    continue
                if preference.time_bucket and session.time_bucket != preference.time_bucket:
                    continue
                if preference.venue and session.venue.name != preference.venue.name:
                    continue
                current_schedule.try_add_session(session, options)

        all_schedules.append(current_schedule)

    best_schedule: Schedule = sorted(all_schedules, key=lambda item: item.calculate_score(options.preferences), reverse=True)[0]

    best_schedule.sort()

    return best_schedule