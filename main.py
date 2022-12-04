from datetime import datetime, time

from get_data import get_sessions

MAX_SESSIONS = 1
FAVOURITE_VENUE = "Light House Cuba"

all_sessions = []

for session in get_sessions():
    session["date"] = datetime.fromisoformat(session["datetime"]).date()
    session["time"] = datetime.fromisoformat(session["datetime"]).time()
    session["day"] = session["date"].strftime("%A")

    match session["date"].weekday():
        case 5 | 6:
            session["day-bucket"] = "we"
        case 4:
            session["day-bucket"] = "fri"
        case 1 | 2 | 3:
            session["day-bucket"] = "wd"
        case _:
            session["day-bucket"] = None

    if session["time"] < time(12):
        session["time-bucket"] = "morning"
    elif session["time"] < time(17):
        session["time-bucket"] = "afternoon"
    elif session["time"] > time(17):
        session["time-bucket"] = "evening"
    else:
        session["time-bucket"] = "other"

    all_sessions.append(session)

total_schedule = []

def add_session(session):
    if any(entry['name'] == session["name"] for entry in total_schedule):
        return
    if len([x for x in total_schedule if x["date"] == session["date"]]) == MAX_SESSIONS:
        return
    total_schedule.append(session)

[add_session(session) for session in all_sessions if (session["day-bucket"] == "we" and session["time-bucket"] == "morning" and session["venue"] == FAVOURITE_VENUE)]
[add_session(session) for session in all_sessions if (session["day-bucket"] == "we" and session["time-bucket"] == "morning")]

[add_session(session) for session in all_sessions if (session["day-bucket"] == "we" and session["time-bucket"] == "afternoon" and session["venue"] == FAVOURITE_VENUE)]
[add_session(session) for session in all_sessions if (session["day-bucket"] == "we" and session["time-bucket"] == "afternoon")]

[add_session(session) for session in all_sessions if (session["day-bucket"] == "fri" and session["time-bucket"] == "evening" and session["venue"] == FAVOURITE_VENUE)]
[add_session(session) for session in all_sessions if (session["day-bucket"] == "fri" and session["time-bucket"] == "evening")]

[add_session(session) for session in all_sessions if (session["day-bucket"] == "wd" and session["time-bucket"] == "evening" and session["venue"] == FAVOURITE_VENUE)]
[add_session(session) for session in all_sessions if (session["day-bucket"] == "wd" and session["time-bucket"] == "evening")]

for event in sorted(total_schedule, key=lambda x: x["datetime"]):
    when = datetime.fromisoformat(event["datetime"]).strftime("%c")
    #print(f"{when}: {event['name']} ({event['venue']}) {event['link']}")
    print(f"{when}: {event['name']} ({event['venue']})")
