import logging
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from src.auth.routes import router as auth_router
from src.user.routes import router as user_router
from src.property.routes import router as property_router
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

# from fastapi import Request

# @app.middleware("http")
# async def log_requests(request: Request, call_next):
#     logging.info(f"Request: {request.method} {request.url}")
#     logging.info(request.form())
#     logging.info(request.values())
#     response = await call_next(request)
#     logging.info(f"Response status: {response.status_code}")
#     return response

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(property_router)
