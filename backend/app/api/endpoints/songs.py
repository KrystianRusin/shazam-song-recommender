import logging
from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import List

router = APIRouter()

logger = logging.getLogger(__name__)

# Define Pydantic model for Songs
class Song(BaseModel):
    id: int
    title: str
    artist: str

# Sample in-memory database for demonstration purposes
songs_db: List[Song] = [
    Song(id=1, title="Song 1", artist="Artist 1"),
    Song(id=2, title="Song 2", artist="Artist 2"),
]

@router.get("/", response_model=List[Song])
async def get_songs():
    logger.info("Retrieving all songs")
    return songs_db

@router.get("/{song_id}", response_model=Song)
async def get_song(song_id: int):
    logger.info("Looking for song with id %s", song_id)
    for song in songs_db:
        if song.id == song_id:
            logger.info("Found song: %s", song)
            return song
    logger.warning("Song with id %s not found", song_id)
    raise HTTPException(status_code=404, detail="Song Not Found")

@router.post("/upload", response_model=Song)
async def upload_song(file: UploadFile = File(...)):
    logger.info(f"Received file upload: {file.filename}")

    # Validate file type again
    if not file.filename.endswith('.mp3'):
        logger.warning(f"Invalid file type:  {file.filename}")
        raise HTTPException(status_code=400, detail="Only MP3 files are accepted")

    try:
        # Read file into memory
        contents = await file.read()
        logger.info(f"Successfully read {len(contents)} bytes from {file.filename}")

        # TODO: Process audio data to create fingerprint
        # 1. Convert MP3 to format librosa can process
        # 2. Create spectrogram
        # 3. Extract features for fingerprinting
        # Example placeholder:
        # audio_fingerprint = create_fingerprint(contents)

        # TODO: Strore fingerprint in database
        # Example placeholder
        # db_id = store_fingerprint_in_db(audio_fingerprint, file.filename)

    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")




