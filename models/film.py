from datetime import timedelta


class Film:
    def __init__(self, name: str, runtime: timedelta, year: int = None) -> None:
        self.name = name
        self.runtime = runtime
        self.year = year