from datetime import timedelta


class Film:
    def __init__(self, name: str, runtime: timedelta) -> None:
        self.name = name
        self.runtime = runtime