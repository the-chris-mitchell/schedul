from models.base import Base
from utils.config import CONFIG

class Venue(Base):
    name: str

    @property
    def normalised_name(self) -> str:
        if CONFIG.normalise_venues:
            for venue in CONFIG.normalise_venues:
                if self.name in venue.match:
                    return venue.replace
        return self.name

    class Config(Base.Config):
        frozen=True