from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn # type: ignore
from clients.sql import create_db_and_tables

from routers import films, screenings, venues, festivals


app = FastAPI(
    title="Schedul",
    docs_url=None,
    redoc_url="/docs"
)

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

@app.on_event("startup") # type: ignore
def on_startup():
    create_db_and_tables()


app.include_router(films.router)
app.include_router(screenings.router)
app.include_router(venues.router)
app.include_router(festivals.router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) # type: ignore