from festivals import FESTIVALS
from models.festival import Festival
from utils.args import ARGS
from utils.format import header

selected_festival: Festival = [festival for festival in FESTIVALS if festival.short_name == ARGS.festival][0]
selected_festival.get_sessions()

match ARGS.mode:
    case "schedule":
        schedule = selected_festival.get_schedule()
        print(header(f"🎬 {selected_festival.full_name}"))
        print(schedule.get_formatted())
        print(header(f"{len(schedule.sessions)} films over {len(list({session.start_time.date() for session in schedule.sessions}))} days"))
    case "sessions":
        print(header(f"🎬 {selected_festival.full_name} sessions"))
        print(selected_festival.get_formatted_sessions())
        print(header(f"{len(selected_festival.sessions)} sessions over {len(list({session.start_time.date() for session in selected_festival.sessions}))} days"))
    case "films":
        print(header(f"🎬 {selected_festival.full_name} films"))
        print(selected_festival.get_formatted_films())
        print(header(f"{len(selected_festival.get_films())} films (watchlist: {len(selected_festival.get_watchlist())})"))
    case "films-csv":
        selected_festival.save_films_csv()
    case "cal":
        selected_festival.get_schedule().save_calendar(f"{ARGS.festival}.ics")
