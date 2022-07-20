from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn # type: ignore
from festivals import FESTIVALS
from models.festival import Festival

from models.film import Film
from models.session import Session
from models.venue import Venue


app = FastAPI()

origins = [
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/festivals")
def get_festivals() -> list[Festival]:
    return FESTIVALS

@app.get("/festivals/{festival_short_name}/films", response_model=set[Film])
def get_films(festival_short_name: str) -> set[Film]:
    festival = [festival for festival in FESTIVALS if festival.short_name == festival_short_name][0]
    return festival.get_films()

@app.get("/festivals/{festival_short_name}/venues", response_model=list[Venue])
def get_venues(festival_short_name: str):
    festival = [festival for festival in FESTIVALS if festival.short_name == festival_short_name][0]
    return festival.get_venues()

@app.get("/festivals/{festival_short_name}/sessions", response_model=list[Session])
def get_sessions(festival_short_name: str):
    festival = [festival for festival in FESTIVALS if festival.short_name == festival_short_name][0]
    return festival.sessions

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) # type: ignore