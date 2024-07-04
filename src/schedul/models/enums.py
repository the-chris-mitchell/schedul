from enum import Enum


class TimeBucket(Enum):
    NONE = "none"
    MORNING = "morning"
    EARLY_AFTERNOON = "early_afternoon"
    LATE_AFTERNOON = "late_afternoon"
    EVENING = "evening"
    LATE = "late"


class DayBucket(Enum):
    NONE = "none"
    WEEKEND = "weekend"
    WEEKDAY = "weekday"
