from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.auth.routes import router as auth_router
from app.user.routes import router as user_router
from app.db import initialize_database, close_database


app = FastAPI(
    title="RealEstate API",
    description="API for RealEstate application",
    version="0.1.0",
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await initialize_database()
    try:
        yield
    finally:
        await close_database()

app.router.lifespan_context = lifespan

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(user_router)