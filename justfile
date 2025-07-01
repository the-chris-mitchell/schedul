setup:
    uv run pre-commit install

start: setup
    uv run uvicorn src.schedul.main:app --reload --port 8001

tui: setup
    uv run textual run --dev src/schedul/tui.py

scrape: setup
    uv run src/schedul/scrape.py

deptry: setup
    uv run deptry .
