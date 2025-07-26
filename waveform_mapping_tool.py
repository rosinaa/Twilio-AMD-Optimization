import pandas as pd
import requests
import matplotlib.pyplot as plt
import numpy as np
from scipy.io import wavfile
import os

# ---------- CONFIGURATION ----------
CSV_FILE = "recording_urls.csv"    # Your CSV input file
URL_COLUMN = "Audio"               # Column in CSV with the .wav URLs
DOWNLOAD_DIR = "downloads"         # Where to store wav files
OUTPUT_FULL = "waveforms_full"     # Full call waveform images
OUTPUT_59S = "waveforms_59s"       # First 59s waveform images
MAX_DURATION_SEC = 59              # For 59s plots
# -----------------------------------

os.makedirs(DOWNLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_FULL, exist_ok=True)
os.makedirs(OUTPUT_59S, exist_ok=True)

def sanitize_filename(url):
    # Basic way to make a safe filename from the URL (could improve)
    return os.path.basename(url).split('?')[0]

def download_wav_to_disk(url, path):
    """Download wav file to disk if not already there."""
    if not os.path.isfile(path):
        resp = requests.get(url, stream=True)
        resp.raise_for_status()
        with open(path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)

def read_audio(filename):
    """Read wav, handle stereo and normalize."""
    sample_rate, data = wavfile.read(filename)
    # Convert to mono if needed
    if data.ndim > 1:
        data = data.mean(axis=1)
    # Normalize to [-1, 1] if integer
    if np.issubdtype(data.dtype, np.integer):
        data = data.astype(np.float32) / np.iinfo(data.dtype).max
    return sample_rate, data

def plot_waveform(data, sample_rate, output_path, title, max_duration=None):
    if max_duration:
        max_samples = int(min(len(data), sample_rate * max_duration))
        data = data[:max_samples]
    time_axis = np.linspace(0, len(data) / sample_rate, num=len(data))
    plt.figure(figsize=(14, 4))
    plt.plot(time_axis, data, color="gray", linewidth=0.8)
    plt.xlabel("Time (seconds)")
    plt.ylabel("Amplitude")
    plt.title(title)
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()

def main():
    df = pd.read_csv(CSV_FILE)
    for idx, row in df.iterrows():
        url = str(row[URL_COLUMN])
        fname = sanitize_filename(url)
        wav_path = os.path.join(DOWNLOAD_DIR, fname)
        print(f"\nProcessing [{idx+1}/{len(df)}]: {url}")
        try:
            # Download
            download_wav_to_disk(url, wav_path)
            # Read
            sample_rate, data = read_audio(wav_path)
            # Plot full waveform
            out_full = os.path.join(OUTPUT_FULL, f"{fname}.png")
            plot_waveform(data, sample_rate, out_full, "Full Call Waveform")
            # Plot 59s waveform
            out_59s = os.path.join(OUTPUT_59S, f"{fname}_59s.png")
            plot_waveform(data, sample_rate, out_59s, f"Waveform (First {MAX_DURATION_SEC}s)", max_duration=MAX_DURATION_SEC)
            print(f"Saved: {out_full} and {out_59s}")
        except Exception as e:
            print(f"Error processing {url}: {e}")

if __name__ == "__main__":
    main()
