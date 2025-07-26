# Twilio AMD Audio Analysis Toolkit

This repository contains tools to analyze Twilio Answering Machine Detection (AMD) performance using `.wav` recordings from real calls. It includes utilities for audio channel separation, event correlation, AMD parameter tuning, and visual inspection of detection behavior.

---

## Setup and Installation

### 1. Clone the Repository

```bash
git clone https://github.com/fvmach/Optimization-Engine.git
cd Optimization-Engine
```

### 2. Install Dependencies

Create a virtual environment (optional):

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

Install required packages:

```bash
pip install -r requirements.txt
```

If a `requirements.txt` is not available, install the dependencies manually:

```bash
pip install pydub numpy scipy matplotlib
```

**Note:** `ffmpeg` must be installed and available in your system's PATH for audio processing with `pydub`.

---

## Script Usage

### `split_channels.py`

This script scans the repository for all `.wav` files, identifies stereo audio, and splits each into separate mono channel files.

**Usage:**

```bash
python split_channels.py
```

**Output:**

* Input: Stereo `.wav` files
* Output: `channel_audio/` folder containing `filename_left.wav` and `filename_right.wav`

---

### `analyze_events.py` (if included)

This script analyzes `.wav` recordings in conjunction with AMD event data (JSON or logs) to produce annotated visualizations.

**Usage:**

```bash
python analyze_events.py
```

**Output:**

* PNG waveform visualizations with markers for speech segments, silence, and AMD detection points

---

## AMD Parameter Tuning

Twilio AMD allows tuning its detection engine using four parameters:

| Parameter                            | Valid Range   | Default |
| ------------------------------------ | ------------- | ------- |
| `MachineDetectionTimeout`            | 3–59 seconds  | 30      |
| `MachineDetectionSpeechThreshold`    | 1000–6000 ms  | 2400    |
| `MachineDetectionSpeechEndThreshold` | 500–5000 ms   | 1200    |
| `MachineDetectionSilenceTimeout`     | 2000–10000 ms | 5000    |

These parameters influence how the AMD engine reacts to detected speech and silence. Adjusting them helps optimize detection accuracy across different voicemail and greeting styles.

**Official documentation:**
[Twilio AMD Optional Parameters](https://www.twilio.com/docs/voice/answering-machine-detection#optional-parameters)

---

## Tools and Analysis Capabilities

This toolkit provides:

* Stereo channel isolation for separate inspection of input and output audio
* Speech and silence segmentation
* Annotated waveform visualization with AMD detection markers
* Parameter impact evaluation across real-world recordings
* Identification of race conditions or detection anomalies

---

## Folder Structure (after processing)

```
.
├── channel_audio/             # Mono channel files (left/right)
├── analysis_*.png             # Annotated waveform plots
├── *.wav                      # Original recordings
├── *.json / *.log             # Optional metadata or AMD event logs
├── split_channels.py
├── analyze_events.py
└── README.md
```

---

## Best Practices for Fine-Tuning

* Use a diverse set of recordings with varying environments and greeting types
* Tune parameters incrementally for precision
* Prefer `AsyncAmd` in production use cases
* Visually validate detection behavior before deploying changes

---

## License

MIT License
© Fernando Vieira Machado
