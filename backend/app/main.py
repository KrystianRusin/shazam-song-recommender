import logging
import sys
import uvicorn
import backend.config.log_config
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.endpoints import songs
from backend.models.database import engine 
from backend.models import song

app = FastAPI()

# Initialize database tables
song.Base.metadata.create_all(bind=engine)

logger = logging.getLogger(__name__)
logger.info("Application startup")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"]
)

app.include_router(songs.router, prefix="/songs", tags=["songs"])

@app.get("/")
async def read_root():
    print("root triggered")
    logger.info("root triggered")
    return {"message": "Hello World"}

