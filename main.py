from datetime import datetime, time

from get_data import get_sessions

from tqdm import tqdm

import random

MAX_SESSIONS = 1
FAVOURITE_VENUE = "Light House Cuba"

preferences = [
    {"day": "weekend", "time": "morning"},
    {"day": "weekend", "time": "afternoon"},
    {"day": "friday", "time": "evening"},
    {"day": "weekend", "time": "evening"},
    {"day": "weekday", "time": "evening"}
]

all_sessions = []

for session in get_sessions():
    session["date"] = datetime.fromisoformat(session["datetime"]).date()
    session["time"] = datetime.fromisoformat(session["datetime"]).time()
    session["day"] = session["date"].strftime("%A")

    match session["date"].weekday():
        case 5 | 6:
            session["day-bucket"] = "weekend"
        case 4:
            session["day-bucket"] = "friday"
        case 1 | 2 | 3:
            session["day-bucket"] = "weekday"
        case _:
            session["day-bucket"] = None

    if session["time"] < time(13):
        session["time-bucket"] = "morning"
    elif session["time"] < time(17):
        session["time-bucket"] = "afternoon"
    elif session["time"] > time(17):
        session["time-bucket"] = "evening"
    else:
        session["time-bucket"] = "other"

    all_sessions.append(session)

all_schedules = []

def valid_session(session, schedule):
    if len(schedule) == 0:
        return True
    if any(entry["name"] == session["name"] for entry in schedule):
        return False
    if len([x for x in schedule if x["date"] == session["date"]]) == MAX_SESSIONS:
        return False
    return True

for x in tqdm(range(1000)):

    current_schedule = []

    shuffled_sessions = random.sample(all_sessions, k=len(all_sessions))

    for preference in preferences:
        [current_schedule.append(session) for session in shuffled_sessions if (valid_session(session, current_schedule) and session["day-bucket"] == preference["day"] and session["time-bucket"] == preference["time"] and session["venue"] == FAVOURITE_VENUE)]
        [current_schedule.append(session) for session in shuffled_sessions if (valid_session(session, current_schedule) and session["day-bucket"] == preference["day"] and session["time-bucket"] == preference["time"])]

    score = 0
    
    for position, _ in enumerate(preferences):
        score += len([session for session in all_sessions if (session["day-bucket"] == preference["day"] and session["time-bucket"] == preference["time"])]) * position

    score += len([session for session in current_schedule if session["venue"] == FAVOURITE_VENUE])

    all_schedules.append({"sessions": current_schedule, "score": score})

best_schedule = sorted(all_schedules, key=lambda item: item["score"], reverse=True)[0]["sessions"]

for event in sorted(best_schedule, key=lambda x: x["datetime"]):
    when = datetime.fromisoformat(event["datetime"]).strftime("%c")
    #print(f"{when}: {event['name']} ({event['venue']}) {event['link']}")
    print(f"{when}: {event['name']} ({event['venue']})")
