from contextlib import asynccontextmanager
from fastapi import FastAPI
from database import get_driver, close_driver
from routers import movie, person, user, genre, company, review, auth, analytics

@asynccontextmanager
async def lifespan(app: FastAPI):
    get_driver()
    yield
    close_driver()

app = FastAPI(title="Movies API", lifespan=lifespan)

# CRUD
app.include_router(movie.router)
app.include_router(person.router)
app.include_router(user.router)
app.include_router(company.router)
app.include_router(review.router)
app.include_router(genre.router)

# Auth
app.include_router(auth.router)

# analytics
app.include_router(analytics.router)
