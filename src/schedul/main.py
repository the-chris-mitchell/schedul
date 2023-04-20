import uvicorn
from clients.sql import create_db_and_tables
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import festivals, films, screenings, venues
from scraper.festivals.custom.example import TestFest

app: FastAPI = FastAPI(title="Schedul", docs_url=None, redoc_url="/docs")

origins: list[str] = ["http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    create_db_and_tables()
    TestFest.create_resources()


app.include_router(films.router)
app.include_router(screenings.router)
app.include_router(venues.router)
app.include_router(festivals.router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
