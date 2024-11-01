import os

DATABASE_URL = "postgresql+asyncpg://%s:%s@%s:%s/%s".format(
    os.getenv("DB_USER"),
    os.getenv("DB_PASSWORD"),
    os.getenv("DB_HOST"),
    os.getenv("DB_PORT"),
    os.getenv("DB_NAME"),
)
