from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from schedul.clients.sql import create_db_and_tables
from schedul.routers import (
    bookings,
    festivals,
    films,
    screenings,
    users,
    venues,
    watchlist,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app: FastAPI = FastAPI(
    title="Schedul", docs_url=None, redoc_url="/docs", lifespan=lifespan
)

origins: list[str] = ["http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(films.router)
app.include_router(screenings.router)
app.include_router(venues.router)
app.include_router(festivals.router)
app.include_router(users.router)
app.include_router(watchlist.router)
app.include_router(bookings.router)
