from abc import ABC, abstractmethod
import random
import csv

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

        for session in sorted(self.sessions, key=lambda x: x.start_time):
            lines.append(session.format())

        return "\n".join(lines)
    def shuffle(self, sessions: list[Session]) -> list[Session]:
        return random.sample(sessions, k=len(sessions))
    
    def get_schedule(self) -> Schedule:

        all_schedules: list[Schedule] = []
        watchlist_sessions = [session for session in self.sessions if session.film.watchlist]
        #watchlist_sessions = [session for session in self.sessions]

        sessions_per_film = Counter(session.film.name for session in watchlist_sessions)

        single_session_films = [key for key, value in sessions_per_film.items() if value == 1]
        one_off_sessions = [session for session in watchlist_sessions if session.film.name in single_session_films]

        multi_session_films = [key for key, value in sessions_per_film.items() if value > 1]
        one_of_many_sessions = [session for session in watchlist_sessions if session.film.name in multi_session_films]

        for _ in tqdm(range(CONFIG.iterations), leave=False, unit="schedule"):
            current_schedule = Schedule()

            booked_sessions = [session for session in self.sessions if session.id in CONFIG.booked_sessions]

            for session in booked_sessions:
                session.book()

            current_schedule.sessions.extend(booked_sessions)

            shuffled_sessions = self.shuffle(one_off_sessions) + self.shuffle(one_of_many_sessions)

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
