import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from src.auth.routes import router as auth_router
from src.user.routes import router as user_router
from src.property.routes import router as property_router
from src.listing.routes import router as listing_router
from src.db import initialize_database, close_database

logging.basicConfig(level=logging.DEBUG)

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
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(property_router)
app.include_router(listing_router)
