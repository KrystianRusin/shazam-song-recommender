import logging
from fastapi import Depends
from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from backend.models.database import get_db
from backend.models.song import Song as SongModel, Fingerprint as FingerprintModel
from backend.utils.audio_processing import convert_to_wav, create_spectrogram, visualize_spectrogram, generate_fingerprint
from typing import List
from sqlalchemy.orm import Session

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
async def upload_song(file: UploadFile = File(...), db: Session = Depends(get_db)):
    logger.info(f"Received file upload: {file.filename}")

    # Validate file type again
    if not (file.filename.endswith('.mp3') or file.filename.endswith('.wav')):
        logger.warning(f"Invalid file type:  {file.filename}")
        raise HTTPException(status_code=400, detail="Only MP3 files are accepted")

    try:
        # Read file into memory
        contents = await file.read()
        logger.info(f"Successfully read {len(contents)} bytes from {file.filename}")

        # TODO: Process audio data to create fingerprint
        # 1. Convert MP3 to format librosa can process (.wav)
        if file.filename.endswith('.mp3'):
            wav_io = convert_to_wav(contents)
            # Verify conversion worked
            wav_data = wav_io.read()
            logger.info(f"Successfully converted to WAV: {len(wav_data)} bytes")
        
        # 2. Create spectrogram
        spectrogram, sampling_rate = create_spectrogram(wav_io)
        #visualize_spectrogram(spectrogram, sampling_rate, save_path="spectrogram.png")

        # 3. Extract features for fingerprinting
        fingerprint = generate_fingerprint(spectrogram)

        song_title = file.filename.replace('.mp3', '').replace('.wav', '')
        new_song = SongModel(title=song_title, artist="Unknown")
        db.add(new_song)
        db.commit()
        db.refresh(new_song)
        
        # Store fingerprints in the database
        for hash_value, offsets in fingerprint.items():
            for offset in offsets:
                new_fp = FingerprintModel(song_id=new_song.id, hash_value=hash_value, offset=int(offset))
                db.add(new_fp)
        db.commit()
        
        return new_song

    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")




