import io
import subprocess
import tempfile
import os
import logging
import numpy as np
import librosa
from io import BytesIO
import matplotlib.pyplot as plt
import librosa.display

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
    
def create_spectrogram(wav_io):
    logger.info("Create spectrogram called")

    wav_io.seek(0)
    # Save audio data to temp file because librosa has trouble with BytesIO object
    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_wav:
        temp_wav.write(wav_io.read())
        temp_wav_path = temp_wav.name

    # Load audio data
    song_data, sampling_rate = librosa.load(temp_wav_path, sr=None)
    logger.info("song_data loaded")

    # Compute the Mel spectrogram (returns power values)
    mel_spec = librosa.feature.melspectrogram(
        y=song_data,
        sr=sampling_rate,
        n_fft=2048,
        hop_length=512
    )
    logger.info("Mel spec created")

    # Convert the power spectrogram to decibel scale
    spectrogram_dB = librosa.power_to_db(mel_spec, ref=np.max)
    logger.info("Covnerted to db")

    return spectrogram_dB, sampling_rate

def visualize_spectrogram(spectrogram_dB, sampling_rate, hop_length=512, save_path=None):
    plt.figure(figsize=(10, 4))
    librosa.display.specshow(
        spectrogram_dB, 
        sr=sampling_rate, 
        hop_length=hop_length,
        x_axis='time', 
        y_axis='mel'
    )
    plt.colorbar(format='%+2.0f dB')
    plt.title('Mel Spectrogram (dB)')
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path)
        plt.close()  
    else:
        plt.show()