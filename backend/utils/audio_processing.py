import io
import subprocess
import tempfile
import os
import logging
import numpy as np
import librosa
import hashlib
import scipy.ndimage as ndimage
import matplotlib.pyplot as plt
import librosa.display
from collections import defaultdict

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
    wav_io.seek(0)
    # Save audio data to temp file because librosa has trouble with BytesIO object
    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_wav:
        temp_wav.write(wav_io.read())
        temp_wav_path = temp_wav.name

    # Load audio data
    song_data, sampling_rate = librosa.load(temp_wav_path, sr=None)

    # Compute the Mel spectrogram (returns power values)
    mel_spec = librosa.feature.melspectrogram(
        y=song_data,
        sr=sampling_rate,
        n_fft=2048,
        hop_length=512
    )

    # Convert the power spectrogram to decibel scale
    spectrogram_dB = librosa.power_to_db(mel_spec, ref=np.max)

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

def detect_local_peaks(spectrogram, threshold_db=-40, neighborhood_size=20):
    
    # Create square footprint of ones
    footprint = np.ones((neighborhood_size, neighborhood_size))

    # Use max filter over spectrogram
    local_max = ndimage.maximum_filter(spectrogram, footprint=footprint)

    # A point is a peak if it equals the local max and is above the threshold
    peaks_max = (spectrogram == local_max) & (spectrogram >= threshold_db)

    # Find coordinates (freq, and time) of these peaks
    peaks = np.argwhere(peaks_max)
    return [tuple(p) for p in peaks]

def find_peaks_in_target_zone(peaks, anchor_peak, min_time_delta=0, max_time_delta=30):
    _, anchor_time = anchor_peak
    target_peaks = [
        peak for peak in peaks
        if (peak[1] - anchor_time) >= min_time_delta and (peak[1] - anchor_time) <= max_time_delta
    ]
    return target_peaks

def create_hash(anchor_freq, target_freq, time_diff):

    # Combine the parameters into a single string.
    hash_input = f"{anchor_freq}-{target_freq}-{time_diff}"
    # Compute the MD5 hash of the input string.
    hash_obj = hashlib.md5(hash_input.encode('utf-8'))
    return hash_obj.hexdigest()

def generate_fingerprint(spectrogram):
    fingerprint = defaultdict(list)
    peaks = detect_local_peaks(spectrogram)
    for peak in peaks:
        anchor_freq, anchor_time = peak  
        target_peaks = find_peaks_in_target_zone(peaks, peak)
        for target_peak in target_peaks:
            target_freq, target_time = target_peak
            time_diff = target_time - anchor_time
            hash_value = create_hash(anchor_freq, target_freq, time_diff)
            fingerprint[hash_value].append(anchor_time)
    return fingerprint