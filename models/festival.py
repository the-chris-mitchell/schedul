from abc import ABC, abstractmethod
import random

import arrow  # type: ignore
from tqdm import tqdm  # type: ignore
from models.options import Options
from models.schedule import Schedule
from models.session import Session


class Festival(ABC):
    def __init__(self) -> None:
        self.sessions: list[Session] = []

    @property
    @abstractmethod
    def full_name(self) -> str:
        pass

    @property
    @abstractmethod
    def short_name(self) -> str:
        pass

    @abstractmethod
    def get_sessions(self) -> None:
        pass

    def get_formatted(self) -> str:
        lines: list[str] = []

        film_names = list({session.film.name for session in self.sessions})

        for film_name in sorted(film_names):
            lines.extend((f"\n🎬 {film_name}:", "─" * 10))
            film_sessions = [session for session in self.sessions if session.film.name == film_name]
            for session in sorted(film_sessions, key=lambda x: x.start_time):
                lines.append(session.format())

        return "\n".join(lines)
    
    def get_schedule(self, options: Options) -> Schedule:

        all_schedules: list[Schedule] = []

        for _ in tqdm(range(options.iterations)):
            current_schedule = Schedule()

            booked_sessions = [session for session in self.sessions if session.link in options.booked_links]

            for session in booked_sessions:
                session.book()

            current_schedule.sessions.extend(booked_sessions)

            shuffled_sessions: list[Session] = random.sample(self.sessions, k=len(self.sessions))

            for preference in options.preferences:
                for session in shuffled_sessions:
                    if session.start_time < arrow.utcnow():
                        continue
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
