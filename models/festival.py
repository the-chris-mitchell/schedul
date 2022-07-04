from abc import ABC, abstractmethod
import random
import csv

import arrow  # type: ignore
from tqdm import tqdm  # type: ignore
from models.schedule import Schedule
from models.session import Session
from models.venue import Venue
from utils.config import CONFIG


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

    def get_formatted_films(self) -> str:
        films = sorted(list({session.film for session in self.sessions}), key=lambda x: x.name)
        lines = []
        watchlist_count = 0
        for film in films:
            formatted_film_elements = [film.name]
            if film.year:
                formatted_film_elements.append(f"({film.year})")
            if film.watchlist:
                formatted_film_elements.append("👀")
                watchlist_count += 1
            lines.append(" ".join(formatted_film_elements))

        lines.extend(("---", f"Watchlist count: {watchlist_count}"))

        return "\n".join(lines)

    def save_films_csv(self) -> None:
        films = list({session.film for session in self.sessions})
        films_dict_list = [{"title": film.name, "year": film.year} for film in films]
        with open(f"{self.short_name}.csv", "w") as file:
            dict_writer = csv.DictWriter(file, films_dict_list[0].keys())
            dict_writer.writeheader()
            dict_writer.writerows(films_dict_list)

    def get_formatted_sessions(self) -> str:
        lines: list[str] = []

        film_names = list({session.film.name for session in self.sessions})

        for film_name in sorted(film_names):
            lines.extend((f"\n🎬 {film_name}:", "─" * 10))
            film_sessions = [session for session in self.sessions if session.film.name == film_name]
            lines.extend(session.format() for session in sorted(film_sessions, key=lambda x: x.start_time))

        return "\n".join(lines)
    
    def get_schedule(self) -> Schedule:

        all_schedules: list[Schedule] = []
        watchlist_sessions = [session for session in self.sessions if session.film.watchlist]

        for _ in tqdm(range(CONFIG.iterations), leave=False, unit="schedule"):
            current_schedule = Schedule()

            booked_sessions = [session for session in watchlist_sessions if session.link in CONFIG.booked_sessions]

            for session in booked_sessions:
                session.book()

            current_schedule.sessions.extend(booked_sessions)

            shuffled_sessions: list[Session] = random.sample(watchlist_sessions, k=len(watchlist_sessions))

            for preference in CONFIG.preferences:
                for session in shuffled_sessions:
                    if preference.date and session.start_time.date() != preference.date:
                        continue
                    if preference.day_bucket and session.day_bucket != preference.day_bucket:
                        continue
                    if preference.time_bucket and session.time_bucket != preference.time_bucket:
                        continue
                    if preference.venue and session.venue.name != preference.venue:
                        continue
                    current_schedule.try_add_session(session)

            for session in shuffled_sessions:
                current_schedule.try_add_session(session)

            all_schedules.append(current_schedule)

        best_schedule: Schedule = sorted(all_schedules, key=lambda item: item.calculate_score(), reverse=True)[0]

        best_schedule.sort()

        return best_schedule
