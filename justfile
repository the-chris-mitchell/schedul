setup:
    uv run pre-commit install

start: setup
    uv run uvicorn src.schedul.main:app --reload --port 8001

tui: setup
    uv run textual run --dev src/schedul/tui.py

scrape env festival: setup
    uv run src/schedul/scrape.py {{env}} {{festival}}

deptry: setup
    uv run deptry .

lint:
    uvx ruff check --fix
    uvx ruff format
