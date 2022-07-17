from abc import ABC, abstractmethod
from collections import Counter
import random
import csv

from tqdm import tqdm # type: ignore
from models.film import Film
from models.schedule import Schedule
from models.session import Session
from models.venue import Venue
from utils.config import CONFIG


class Festival(ABC):
    def __init__(self) -> None:
        self.sessions: set[Session] = set()
        
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

    def get_films(self) -> set[Film]:
        return set(sorted({session.film for session in self.sessions}, key=lambda x: x.name))

    def get_venues(self) -> set[Venue]:
        return set(sorted({session.venue for session in self.sessions}, key=lambda x: x.name))

    def get_watchlist(self) -> set[Film]:
        return {film for film in self.get_films() if film.watchlist}

    def get_formatted_films(self) -> str:
        lines: list[str] = []
        for film in self.get_films():
            formatted_film_elements = [film.name]
            if film.year:
                formatted_film_elements.append(f"({film.year})")
            if film.watchlist:
                formatted_film_elements.append("👀")
            lines.append(" ".join(formatted_film_elements))

        return "\n".join(lines)

    def save_films_csv(self) -> None:
        films_dict_list = [{"title": film.name, "year": film.year} for film in self.get_films()]
        with open(f"../../{self.short_name}.csv", "w") as file:
            dict_writer = csv.DictWriter(file, films_dict_list[0].keys())
            dict_writer.writeheader()
            dict_writer.writerows(films_dict_list)

    def get_formatted_sessions(self) -> str:
        lines: list[str] = [session.formatted for session in sorted(self.sessions, key=lambda x: x.start_time)]
        return "\n".join(lines)

    def shuffle(self, sessions: set[Session]) -> set[Session]:
        return set(random.sample(sessions, k=len(sessions)))
    
    def get_schedule(self) -> Schedule:

        all_schedules: list[Schedule] = []
        watchlist_sessions = {session for session in self.sessions if session.film.watchlist}
        non_watchlist_sessions = {session for session in self.sessions if not session.film.watchlist}

        sessions_per_watchlist_film = Counter(session.film.name for session in watchlist_sessions)

        single_session_watchlist_films = {key for key, value in sessions_per_watchlist_film.items() if value == 1}
        one_off_watchlist_sessions = {session for session in watchlist_sessions if session.film.name in single_session_watchlist_films}

        multi_session_watchlist_films = {key for key, value in sessions_per_watchlist_film.items() if value > 1}
        one_of_many_watchlist_sessions = {session for session in watchlist_sessions if session.film.name in multi_session_watchlist_films}

        booked_sessions = {session for session in self.sessions if session.id in CONFIG.booked_sessions}

        for session in booked_sessions:
            session.book()

        for _ in tqdm(range(CONFIG.iterations), leave=False, unit="schedule"):
            current_schedule = Schedule()

            current_schedule.sessions.extend(booked_sessions)

            shuffled_sessions = self.shuffle(one_off_watchlist_sessions) | self.shuffle(one_of_many_watchlist_sessions) | self.shuffle(non_watchlist_sessions)

            for preference in CONFIG.preferences:
                for session in shuffled_sessions:
                    if preference.date and session.start_time.date() != preference.date:
                        continue
                    if preference.day_bucket and session.day_bucket != preference.day_bucket:
                        continue
                    if preference.time_bucket and session.time_bucket != preference.time_bucket:
                        continue
                    if preference.venue and session.venue.normalised_name != preference.venue:
                        continue
                    current_schedule.try_add_session(session)

            for session in shuffled_sessions:
                current_schedule.try_add_session(session)

            all_schedules.append(current_schedule)

        best_schedule: Schedule = sorted(all_schedules, key=lambda item: item.calculate_score(), reverse=True)[0]

        best_schedule.sort()

        return best_schedule
