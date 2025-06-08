start:
    uvicorn src.schedul.main:app --reload --port 8001

tui:
    textual run --dev src/schedul/tui.py

scrape:
    src/schedul/scrape.py

deptry:
    deptry .