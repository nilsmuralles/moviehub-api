from contextlib import asynccontextmanager
from fastapi import FastAPI
from database import get_driver, close_driver
from routers import movie, person, user

@asynccontextmanager
async def lifespan(app: FastAPI):
    get_driver()
    yield
    close_driver()

app = FastAPI(title="Movies API", lifespan=lifespan)

app.include_router(movie.router)
app.include_router(person.router)
app.include_router(user.router)
