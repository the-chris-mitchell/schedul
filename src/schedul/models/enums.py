from enum import Enum


class TimeBucket(Enum):
    NONE = "none"
    MORNING = "morning"
    AFTERNOON = "afternoon"
    EVENING = "evening"

class DayBucket(Enum):
    NONE = "none"
    WEEKEND = "weekend"
    WEEKDAY = "weekday"
    FRIDAY = "friday"