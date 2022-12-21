from clients.sql import engine
from models.festival import Festival
from sqlmodel import Session, select


def create_festival(full_name: str, short_name: str) -> Festival:
    with Session(engine) as session:
        db_festival = Festival(full_name=full_name, short_name=short_name)
        session.add(db_festival)
        session.commit()
        session.refresh(db_festival)
        return db_festival


def create_festival_if_required(full_name: str, short_name: str) -> Festival:
    with Session(engine) as session:
        query = session.exec(
            select(Festival).where(Festival.short_name == short_name)
        ).first()
        return query or create_festival(full_name=full_name, short_name=short_name)


# class Festival(ABC, Base):
#     @property
#     @abstractmethod
#     def full_name(self) -> str:
#         pass

#     @property
#     @abstractmethod
#     def short_name(self) -> str:
#         pass

#     @cached_property
#     @abstractmethod
#     def sessions(self) -> list[Session]:
#         pass

#     def get_films(self) -> set[Film]:
#         return set(sorted({session.film for session in self.sessions}, key=lambda x: x.name))

#     def get_venues(self) -> set[Venue]:
#         return set(sorted({session.venue for session in self.sessions}, key=lambda x: x.name))

#     def get_watchlist(self) -> set[Film]:
#         return {film for film in self.get_films() if film.watchlist}

#     def get_formatted_films(self) -> str:
#         lines: list[str] = []
#         for film in self.get_films():
#             formatted_film_elements = [film.name]
#             if film.year:
#                 formatted_film_elements.append(f"({film.year})")
#             if film.watchlist:
#                 formatted_film_elements.append("👀")
#             lines.append(" ".join(formatted_film_elements))

#         return "\n".join(lines)

#     def save_films_csv(self) -> None:
#         films_dict_list = [{"title": film.name, "year": film.year} for film in self.get_films()]
#         with open(f"../../{self.short_name}.csv", "w") as file:
#             dict_writer = csv.DictWriter(file, films_dict_list[0].keys())
#             dict_writer.writeheader()
#             dict_writer.writerows(films_dict_list)

#     def get_formatted_sessions(self) -> str:
#         lines: list[str] = [f"{session.id}: {session.formatted}" for session in sorted(self.sessions, key=lambda x: x.start_time)]
#         return "\n".join(lines)

#     def shuffle(self, sessions: list[Session]) -> list[Session]:
#         return random.sample(sessions, k=len(sessions))

#     def get_booked_schedule(self) -> Schedule:
#         booked_sessions = [session for session in self.sessions if session.id in CONFIG.booked_sessions]
#         for session in booked_sessions:
#             session.book()
#         schedule = Schedule()
#         schedule.sessions.extend(booked_sessions)
#         return schedule

#     def get_schedule(self) -> Schedule:

#         all_schedules: list[Schedule] = []
#         watchlist_sessions = [session for session in self.sessions if session.film.watchlist]
#         non_watchlist_sessions = [session for session in self.sessions if not session.film.watchlist]

#         sessions_per_watchlist_film = Counter(session.film.name for session in watchlist_sessions)

#         single_session_watchlist_films = {key for key, value in sessions_per_watchlist_film.items() if value == 1}
#         one_off_watchlist_sessions = [session for session in watchlist_sessions if session.film.name in single_session_watchlist_films]

#         multi_session_watchlist_films = {key for key, value in sessions_per_watchlist_film.items() if value > 1}
#         one_of_many_watchlist_sessions = [session for session in watchlist_sessions if session.film.name in multi_session_watchlist_films]

#         booked_sessions = [session for session in self.sessions if session.id in CONFIG.booked_sessions]

#         for session in booked_sessions:
#             session.book()

#         for _ in tqdm(range(CONFIG.iterations), leave=False, unit="schedule"): # type: ignore
#             current_schedule = Schedule()

#             current_schedule.sessions.extend(booked_sessions)

#             shuffled_sessions = self.shuffle(one_off_watchlist_sessions) + self.shuffle(one_of_many_watchlist_sessions) + self.shuffle(non_watchlist_sessions)

#             for preference in CONFIG.preferences:
#                 for session in shuffled_sessions:
#                     if preference.date and session.start_time.date() != preference.date:
#                         continue
#                     if preference.day_bucket and session.day_bucket != preference.day_bucket:
#                         continue
#                     if preference.time_bucket and session.time_bucket != preference.time_bucket:
#                         continue
#                     if preference.venue and session.venue.normalised_name != preference.venue:
#                         continue
#                     current_schedule.try_add_session(session)

#             for session in shuffled_sessions:
#                 current_schedule.try_add_session(session)

#             all_schedules.append(current_schedule)

#         best_schedule: Schedule = sorted(all_schedules, key=lambda item: item.calculate_score(), reverse=True)[0]

#         best_schedule.sort()

#         return best_schedule

#     class Config(Base.Config):
#         frozen=True
