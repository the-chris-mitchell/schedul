from enum import Enum


class TimeBucket(Enum):
    NONE = 0
    MORNING = 1
    AFTERNOON = 2
    EVENING = 3

class DayBucket(Enum):
    NONE = 0
    WEEKEND = 1
    WEEKDAY = 2
    FRIDAY = 3