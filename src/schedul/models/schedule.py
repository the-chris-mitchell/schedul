from datetime import timedelta

import arrow
from ics import Calendar, Event  # type: ignore

from models.session import Session
from utils.config import CONFIG


class Schedule:
    def __init__(self) -> None:
        self.sessions: list[Session] = []
    
    def calculate_score(self) -> float:
        score: float = 0
        for position, preference in enumerate(CONFIG.preferences, start=1):
            position_score = 0
            if preference.date:
                position_score += len([session for session in self.sessions if session.start_time.date() == preference.date])
            if preference.day_bucket:
                position_score += len([session for session in self.sessions if session.day_bucket == preference.day_bucket])
            if preference.time_bucket:
                position_score += len([session for session in self.sessions if session.time_bucket == preference.time_bucket])
            if preference.venue:
                position_score += len([session for session in self.sessions if session.venue.normalised_name == preference.venue])

            score += position_score / position

        return score

    def sort(self) -> None:
        self.sessions = sorted(self.sessions, key=lambda x: x.start_time)

    def get_formatted(self) -> str:
        lines: list[str] = []

        for position, week in enumerate(sorted(list({session.start_time.isocalendar()[1] for session in self.sessions})), start=1):
            lines.append((f" 📆 Week {position} ".center(80, "-")))
            lines.extend(f"{'➕' if session.film.name not in CONFIG.watchlist else ''}{session.formatted}" for session in [session for session in self.sessions if session.start_time.isocalendar()[1] == week])
            lines.append("\n")

        not_picked_in_watchlist = [film for film in CONFIG.watchlist if film not in [session.film.name for session  in self.sessions]]
        lines.append(f"❌ Missing {len(not_picked_in_watchlist)} from watchlist: " + ", ".join(not_picked_in_watchlist))

        return "\n".join(lines)
    
    def save_calendar(self, filename: str) -> None:
        calendar = Calendar()
        for session in self.sessions:
            event = Event()
            event.name = session.film.name
            event.begin = arrow.get(session.start_time).to('utc')
            event.end = arrow.get(session.end_time).to('utc')
            event.location = session.venue.normalised_name
            calendar.events.add(event)
        with open(f"../../{filename}", 'w') as file:
            file.writelines(calendar)  # type: ignore
        print(f"Saved calendar to {filename}")

    def try_add_session(self, session: Session) -> None:
        if session.start_time < arrow.utcnow():
            return
        if session.start_time.date() in CONFIG.excluded_dates:
            return
        if any(entry.film.name == session.film.name for entry in self.sessions):
            return
        if any(entry.start_time <= (session.end_time + timedelta(minutes=CONFIG.buffer_time)) and session.start_time <= (entry.end_time + timedelta(minutes=CONFIG.buffer_time)) for entry in self.sessions):
            return
        if len([x for x in self.sessions if x.start_time.date() == session.start_time.date()]) >= CONFIG.max_sessions:
            return
        self.sessions.append(session)
