import logging
import sys
import uvicorn
import backend.config.log_config
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.endpoints import songs

app = FastAPI()

logger = logging.getLogger(__name__)
logger.info("Application startup")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(songs.router, prefix="/songs", tags=["songs"])

@app.get("/")
async def read_root():
    print("root triggered")
    logger.info("root triggered")
    return {"message": "Hello World"}

