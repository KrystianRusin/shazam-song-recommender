import io
import subprocess
import tempfile
import os
import logging
import numpy as np

logger = logging.getLogger(__name__)

def convert_to_wav(mp3_bytes):
    """
    Convert MP3 bytes to WAV format using FFmpeg
    """
    logger.info("Converting file")
    # Create temporary files for input and output
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_in:
        temp_in.write(mp3_bytes)
        temp_in_path = temp_in.name
    
    temp_out_path = temp_in_path.replace('.mp3', '.wav')
    
    # Use FFmpeg to convert
    try:
        logger.info(f"Converting {temp_in_path} to {temp_out_path}")
        subprocess.run([
            'ffmpeg', '-i', temp_in_path, 
            '-acodec', 'pcm_s16le', '-ar', '44100', temp_out_path
        ], check=True, capture_output=True, text=True)
        
        # Read the wav file
        with open(temp_out_path, 'rb') as f:
            wav_bytes = f.read()
        
        # Clean up temp files
        os.unlink(temp_in_path)
        os.unlink(temp_out_path)
        
        # Return bytes as BytesIO
        wav_io = io.BytesIO(wav_bytes)
        wav_io.seek(0)
        return wav_io
    
    except Exception as e:
        # Clean up temp files
        if os.path.exists(temp_in_path):
            os.unlink(temp_in_path)
        if os.path.exists(temp_out_path):
            os.unlink(temp_out_path)
        logger.error(f"FFmpeg conversion failed: {e}")
        raise Exception(f"FFmpeg conversion failed: {e}")
    

    