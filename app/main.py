from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from .db.session import dispose_engine, ensure_initialized
from .routers.api import api_router
from .seed.loader import seed_if_needed


@asynccontextmanager
async def lifespan(app: FastAPI):
    await ensure_initialized()
    await seed_if_needed()
    try:
        yield
    finally:
        await dispose_engine()


app = FastAPI(title="DataFactory API", version="1.0.0", lifespan=lifespan)

app.include_router(api_router)
