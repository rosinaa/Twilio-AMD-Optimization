import os
from pydub import AudioSegment
from pathlib import Path

# --- Config ---
SOURCE_DIR = Path("recordings")  # or specify your repo folder
OUTPUT_DIR_LEFT = Path("channel_audio/left")
OUTPUT_DIR_RIGHT = Path("channel_audio/right")
OUTPUT_DIR_LEFT.mkdir(exist_ok=True)
OUTPUT_DIR_RIGHT.mkdir(exist_ok=True)

# --- Process All WAV Files ---
def split_channels_in_repo():
    for root, _, files in os.walk(SOURCE_DIR):
        for file in files:
            if file.lower().endswith(".wav"):
                wav_path = Path(root) / file
                process_wav(wav_path)

# --- Split Stereo WAV File ---
def process_wav(wav_path):
    try:
        audio = AudioSegment.from_wav(wav_path)
        if audio.channels != 2:
            print(f"[SKIP] {wav_path} is not stereo.")
            return

        base_name = wav_path.stem
        left_channel = audio.split_to_mono()[0]
        right_channel = audio.split_to_mono()[1]

        left_path = OUTPUT_DIR_LEFT / f"{base_name}_left.wav"
        right_path = OUTPUT_DIR_RIGHT / f"{base_name}_right.wav"

        left_channel.export(left_path, format="wav")
        right_channel.export(right_path, format="wav")

        print(f"[OK] Split {wav_path} -> {left_path}, {right_path}")

    except Exception as e:
        print(f"[ERROR] Could not process {wav_path}: {e}")

# --- Run ---
if __name__ == "__main__":
    split_channels_in_repo()
