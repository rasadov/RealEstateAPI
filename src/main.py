from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from src.auth.routes import router as auth_router
from src.db import initialize_database


app = FastAPI()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await initialize_database()
    try:
        yield
    finally:
        await app.state.engine.dispose()

app.router.lifespan_context = lifespan    

app.include_router(auth_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
