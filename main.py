from datetime import datetime, time

from get_data import get_sessions

MAX_SESSIONS = 1

sessions = []

for session in get_sessions():
    session["date"] = datetime.fromisoformat(session["datetime"]).date()
    session["time"] = datetime.fromisoformat(session["datetime"]).time()
    session["day"] = session["date"].strftime("%A")

    session["score"] = 0

    if session["venue"] == "Light House Cuba":
        session["score"] += 5

    match session["date"].weekday():
        case 5 | 6:
            if session["time"] < time(17):
                session["score"] += 10
            if session["time"] < time(12):
                session["score"] += 15
        case 4:
            session["score"] += 2
        case 1 | 2 | 3 | 4:
            if session["time"] > time(18):
                session["score"] += 1
        case 0:
            session["score"] = 0

    sessions.append(session)

schedule = []

sorted_sessions = sorted(sessions, key=lambda x: x["score"],reverse=True)

for session in sorted_sessions:
    if any(entry['name'] == session["name"] for entry in schedule):
        continue
    if len([x for x in schedule if x["date"] == session["date"]]) == MAX_SESSIONS:
        continue

    schedule.append(session)

for event in sorted(schedule, key=lambda x: x["datetime"]):
    when = datetime.fromisoformat(event["datetime"]).strftime("%c")
    #print(f"{when}: {event['name']} ({event['venue']}) {event['link']}")
    print(f"{when}: {event['name']} ({event['venue']})")