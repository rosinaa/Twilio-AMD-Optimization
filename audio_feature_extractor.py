import os
import pandas as pd
import numpy as np
import librosa
import requests

# CONFIG
CSV_FILE = "recording_urls.csv"
AUDIO_COL = "Audio"
OUTPUT_DIR = "downloads"
FEATURES_OUT = "machine_features.csv"

os.makedirs(OUTPUT_DIR, exist_ok=True)

def download_wav(url, output_path):
    if os.path.exists(output_path):
        return
    r = requests.get(url)
    with open(output_path, "wb") as f:
        f.write(r.content)

def extract_features(file_path):
    y, sr = librosa.load(file_path, sr=None)
    y = y / np.max(np.abs(y))
    abs_y = np.abs(y)
    threshold = 0.03

    # Initial silence
    first_voice_idx = np.argmax(abs_y > threshold)
    initial_silence = first_voice_idx / sr

    # Speech/silence alternations
    voiced = abs_y > threshold
    changes = np.diff(voiced.astype(int))
    starts = np.where(changes == 1)[0]
    ends = np.where(changes == -1)[0]
    speech_alternations = min(len(starts), len(ends))

    # First utterance length
    if len(starts) > 0 and len(ends) > 0:
        utterance_start = starts[0]
        utterance_end = ends[ends > utterance_start][0] if np.any(ends > utterance_start) else len(y)
        first_utterance_len = (utterance_end - utterance_start) / sr
    else:
        first_utterance_len = 0.0

    # Mean/max amplitude
    mean_amp = np.mean(abs_y)
    max_amp = np.max(abs_y)

    # Zero crossing rate
    zcr = np.mean(librosa.feature.zero_crossing_rate(y)[0])

    duration = len(y) / sr

    return {
        "initial_silence_sec": initial_silence,
        "first_utterance_sec": first_utterance_len,
        "speech_alternations": speech_alternations,
        "mean_amp": mean_amp,
        "max_amp": max_amp,
        "zcr": zcr,
        "duration_sec": duration,
    }

def main():
    df = pd.read_csv(CSV_FILE)
    features = []
    for idx, row in df.iterrows():
        url = row[AUDIO_COL]
        filename = os.path.basename(url.split("?")[0])
        local_path = os.path.join(OUTPUT_DIR, filename)
        print(f"Downloading {url} ...")
        download_wav(url, local_path)
        print(f"Extracting features for {filename} ...")
        feats = extract_features(local_path)
        feats['filename'] = filename
        feats['label'] = "machine"
        features.append(feats)
    pd.DataFrame(features).to_csv(FEATURES_OUT, index=False)
    print(f"Saved features to {FEATURES_OUT}")

if __name__ == "__main__":
    main()
