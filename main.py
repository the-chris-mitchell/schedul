from datetime import datetime
import itertools

movies = [
    {"name": "movie1", "time": "2011-11-04T00:05:23"},
    {"name": "movie1", "time": "2011-12-04T00:05:23"},
    {"name": "movie2", "time": "2011-11-04T00:05:23"},
    {"name": "movie2", "time": "2011-14-04T00:05:23"},
    {"name": "movie3", "time": "2011-14-04T00:05:23"},
    {"name": "movie3", "time": "2011-11-04T00:05:23"},
]

schedules = []       

permutations = itertools.permutations(movies, len(movies))

for permutation in permutations:
    schedule = {}
    for p in permutation:
        movie = p["name"]
        time = p["time"]
        if movie in schedule.keys():
            continue
        if time in schedule.values():
            continue
        schedule[movie] = time
    schedules.append(schedule)


sorted_schedules = sorted(schedules, key=len)

print(sorted_schedules[-1])