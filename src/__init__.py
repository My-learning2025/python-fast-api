from fastapi import FastAPI
from src.books.route import book_router
from contextlib import asynccontextmanager
from src.db.main import init_db
from .users.routes import user_router
from .auth.route import auth_router


@asynccontextmanager
async def life_span(app: FastAPI):
    print("server is starting ...")
    await init_db()
    yield
    print("server has been stopped")


version = "v1"
app = FastAPI(title="Book API", version=version, lifespan=life_span)

app.include_router(book_router, prefix=f"/{version}/books", tags=["books"])
app.include_router(user_router, prefix=f"/{version}/users", tags=["users"])
app.include_router(auth_router, prefix=f"/{version}/auth", tags=["auth"])
