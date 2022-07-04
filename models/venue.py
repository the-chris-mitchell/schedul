from utils.config import CONFIG

class Venue:
    def __init__(self, name: str) -> None:
        self.name = self.normalise_name(name)

    @staticmethod
    def normalise_name(name: str) -> str:
        for venue in CONFIG.normalise_venues:
            if name in venue["match"]:
                return venue["replace"]
        return name