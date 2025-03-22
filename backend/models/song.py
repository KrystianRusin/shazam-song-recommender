from sqlalchemy import Column, Integer, String, LargeBinary, ForeignKey, DateTime, Float, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class Song(Base):
    __tablename__ = "songs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    artist = Column(String, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship with fingerprints
    fingerprints = relationship("Fingerprint", back_populates="song")

class Fingerprint(Base):
    __tablename__ = "fingerprints"
    
    id = Column(Integer, primary_key=True, index=True)
    song_id = Column(Integer, ForeignKey("songs.id"))
    hash_value = Column(String, index=True)
    offset = Column(Integer)
    
    # Relationship with song
    song = relationship("Song", back_populates="fingerprints")