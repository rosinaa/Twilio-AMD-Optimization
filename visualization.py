import librosa
import numpy as np
import matplotlib.pyplot as plt
import os

def analyze_and_plot(filepath, save_path=None, threshold=0.03, silence_gap_min=0.4, silence_gap_max=2.5):
    # 1. Load audio
    y, sr = librosa.load(filepath, sr=None)
    abs_y = np.abs(y) / np.max(np.abs(y))
    time = np.arange(len(y)) / sr

    # 2. Voice activity detection
    voiced = abs_y > threshold
    changes = np.diff(voiced.astype(int))
    starts = np.where(changes == 1)[0] + 1
    ends = np.where(changes == -1)[0] + 1

    # 3. Initial silence (before first speech)
    t1 = starts[0] / sr if len(starts) else 0
    t0 = 0

    # 4. Find utterance (first speech to end of last speech)
    if len(ends) and ends[-1] > starts[0]:
        t4 = ends[-1] / sr
    else:
        t4 = len(y) / sr

    # 5. Find internal silence gaps
    silence_gaps = []
    for i in range(1, len(starts)):
        gap = (starts[i] - ends[i-1]) / sr
        if silence_gap_min < gap < silence_gap_max:
            silence_gaps.append((ends[i-1]/sr, starts[i]/sr))

    # 6. Final silence (after last utterance)
    t5 = len(y) / sr

    # 7. Plot
    plt.figure(figsize=(15, 5))
    plt.plot(time, y, color='gray', linewidth=0.8)
    plt.xlabel("Time (seconds)")
    plt.ylabel("Amplitude")
    plt.title(f"AMD-style Analysis of Call\n{os.path.basename(filepath)}")

    # Initial silence
    plt.axvspan(t0, t1, color='green', alpha=0.2, label='Initial Silence')
    # Utterance
    plt.axvspan(t1, t4, color='orange', alpha=0.15, label='Utterance')
    # Silence gaps
    for idx, (gap_start, gap_end) in enumerate(silence_gaps):
        plt.axvspan(gap_start, gap_end, color='blue', alpha=0.2, label='Silence Gap' if idx == 0 else "")
    # Final silence
    plt.axvspan(t4, t5, color='blue', alpha=0.1, label='Final Silence')

    plt.legend(loc="upper right")
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path)
        plt.close()
    else:
        plt.show()

    # Print timings for reference
    print(f"File: {os.path.basename(filepath)}")
    print(f"  Initial silence: {t0:.2f}s to {t1:.2f}s")
    print(f"  Utterance: {t1:.2f}s to {t4:.2f}s")
    print(f"  Silence gaps: {[f'{g[0]:.2f}-{g[1]:.2f}s' for g in silence_gaps]}")
    print(f"  Final silence: {t4:.2f}s to {t5:.2f}s")
    print('-'*60)

def batch_analyze(input_dir='downloads', output_dir='analysis', threshold=0.03):
    os.makedirs(output_dir, exist_ok=True)
    wav_files = [f for f in os.listdir(input_dir) if f.lower().endswith('.wav')]
    print(f"Found {len(wav_files)} wav files in {input_dir}/")
    for wav in wav_files:
        in_path = os.path.join(input_dir, wav)
        out_path = os.path.join(output_dir, f'analysis_{os.path.splitext(wav)[0]}.png')
        analyze_and_plot(in_path, save_path=out_path, threshold=threshold)

if __name__ == "__main__":
    batch_analyze(input_dir="downloads", output_dir="analysis", threshold=0.03)
